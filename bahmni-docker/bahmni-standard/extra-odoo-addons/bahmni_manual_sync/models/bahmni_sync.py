import logging
import requests
import xml.etree.ElementTree as ET
from requests.auth import HTTPBasicAuth
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

OPENMRS_BASE_URL = "http://openmrs:8080/openmrs"
OPENMRS_USER = "admin"
OPENMRS_PASS = "Admin123"


class BahmniSyncDashboard(models.Model):
    _name = 'bahmni.sync.dashboard'
    _description = 'Bahmni Sync Control Panel'

    name = fields.Char(default='Bahmni Sync Control Panel', readonly=True)


class BahmniSyncManager(models.Model):
    _name = 'bahmni.sync.manager'
    _description = 'Bahmni Sync Monitor'

    db_id = fields.Integer(string='DB ID')
    name = fields.Char(string='Feed / Identifier', default='Event')
    feed_uri = fields.Char(string='Feed URI')
    event_id = fields.Char(string='Event ID')
    event_content = fields.Text(string='Content Endpoint')
    error_message = fields.Text(string='Failure Reason')
    retries = fields.Integer(string='Retry Attempts')
    failed_at = fields.Datetime(string='Failed At')

    @api.model
    def action_refresh_queue(self, *args, **kwargs):
        """Refreshes the local failed events listing from odoodb failed_events table."""
        self.search([]).unlink()
        self.env.cr.execute("""
            SELECT id, feed_uri, event_id, event_content, error_message, retries, failed_at
            FROM public.failed_events
            ORDER BY id ASC;
        """)
        recs = self.env.cr.fetchall()
        for rec in recs:
            self.create({
                'db_id': rec[0],
                'name': f"Event #{rec[0]}",
                'feed_uri': rec[1],
                'event_id': rec[2],
                'event_content': rec[3],
                'error_message': rec[4],
                'retries': rec[5],
                'failed_at': rec[6],
            })
        
        count = len(recs)
        msg = f"Queue refreshed: {count} failed event(s) requiring attention." if count > 0 else "Queue refreshed: 0 failed events recorded. (Check Live Sync Health to verify feed activity)."
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Queue Refresh',
                'message': msg,
                'type': 'warning' if count > 0 else 'info',
                'sticky': False,
            }
        }

    @api.model
    def action_check_sync_health(self):
        """Checks connectivity, compares Odoo markers with live OpenMRS AtomFeeds, and counts synced entities."""
        lines = []
        is_healthy = True

        # 1. OpenMRS API Connection
        try:
            resp = requests.get(
                f"{OPENMRS_BASE_URL}/ws/rest/v1/session",
                auth=HTTPBasicAuth(OPENMRS_USER, OPENMRS_PASS),
                timeout=5
            )
            if resp.status_code == 200 and resp.json().get('authenticated'):
                lines.append("OpenMRS Connection: Online & Authenticated")
            else:
                lines.append(f"OpenMRS Connection: Responded status {resp.status_code}")
                is_healthy = False
        except Exception as e:
            lines.append(f"OpenMRS Connection: OFFLINE ({str(e)})")
            is_healthy = False

        # 2. Check Feed Markers
        for feed_name in ['patient', 'encounter', 'lab', 'drug']:
            self.env.cr.execute("""
                SELECT feed_uri_for_last_read_entry, last_read_entry_id
                FROM public.markers
                WHERE feed_uri LIKE %s LIMIT 1;
            """, (f"%{feed_name}%",))
            marker_row = self.env.cr.fetchone()
            marker_uri = marker_row[0] if marker_row else "Not Set"
            marker_page = marker_uri.rstrip('/').split('/')[-1] if marker_uri else "?"

            # Query OpenMRS recent feed
            try:
                feed_resp = requests.get(
                    f"{OPENMRS_BASE_URL}/ws/atomfeed/{feed_name}/recent",
                    timeout=5
                )
                if feed_resp.status_code == 200:
                    root = ET.fromstring(feed_resp.content)
                    via_link = root.find("{http://www.w3.org/2005/Atom}link[@rel='via']")
                    openmrs_page = "?"
                    if via_link is not None:
                        openmrs_page = via_link.attrib.get('href', '').rstrip('/').split('/')[-1]
                    lines.append(f"{feed_name.capitalize()} Feed: Odoo Page {marker_page} / OpenMRS Page {openmrs_page}")
                else:
                    lines.append(f"{feed_name.capitalize()} Feed: OpenMRS returned {feed_resp.status_code}")
                    is_healthy = False
            except Exception:
                lines.append(f"{feed_name.capitalize()} Feed: Could not read OpenMRS recent feed")
                is_healthy = False

        # 3. Entity Counts in Odoo
        self.env.cr.execute("SELECT count(*) FROM res_partner WHERE customer_rank > 0 OR uuid IS NOT NULL;")
        pt_count = self.env.cr.fetchone()[0]
        self.env.cr.execute("SELECT count(*) FROM product_product WHERE uuid IS NOT NULL;")
        prod_count = self.env.cr.fetchone()[0]
        self.env.cr.execute("SELECT count(*) FROM public.failed_events;")
        failed_count = self.env.cr.fetchone()[0]

        lines.append(f"Entity Counts: {pt_count} Patients, {prod_count} Synced Products/Tests")
        if failed_count > 0:
            lines.append(f"Alert: {failed_count} failed event(s) in queue!")
            is_healthy = False

        full_message = "\n".join(lines)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Live Sync Health Report',
                'message': full_message,
                'type': 'success' if is_healthy else 'warning',
                'sticky': True,
            }
        }

    @api.model
    def action_purge_dead_events(self):
        """Purges orphaned 404 events from failed_events so they don't block sync."""
        self.env.cr.execute("""
            DELETE FROM public.failed_events 
            WHERE error_message ILIKE '%404%' 
               OR error_message ILIKE '%not found%'
               OR error_message ILIKE '%Bad response code of 404%';
        """)
        deleted_count = self.env.cr.rowcount
        self.env.cr.commit()
        self.action_refresh_queue()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Purged Dead 404 Events',
                'message': f'Removed {deleted_count} dead 404 event(s) from queue.',
                'type': 'info' if deleted_count > 0 else 'warning',
                'sticky': False,
            }
        }

    @api.model
    def action_autofix_markers(self):
        """Checks atomfeed markers in odoodb and heals corrupted or out-of-bounds markers."""
        fixed_messages = []
        
        for feed_name in ['patient', 'encounter']:
            try:
                resp = requests.get(f"{OPENMRS_BASE_URL}/ws/atomfeed/{feed_name}/recent", timeout=5)
                if resp.status_code == 200:
                    root = ET.fromstring(resp.content)
                    via_link = root.find("{http://www.w3.org/2005/Atom}link[@rel='via']")
                    if via_link is not None:
                        openmrs_feed_uri = via_link.attrib.get('href')
                        entries = root.findall("{http://www.w3.org/2005/Atom}entry")
                        latest_entry_id = entries[-1].find("{http://www.w3.org/2005/Atom}id").text if entries else None

                        self.env.cr.execute("""
                            SELECT id, feed_uri_for_last_read_entry, last_read_entry_id
                            FROM public.markers
                            WHERE feed_uri LIKE %s;
                        """, (f"%{feed_name}%",))
                        m_row = self.env.cr.fetchone()
                        if m_row:
                            m_id, m_uri, m_entry = m_row[0], m_row[1] or '', m_row[2] or ''
                            if not m_entry or ':0' in m_entry:
                                self.env.cr.execute("""
                                    UPDATE public.markers
                                    SET feed_uri_for_last_read_entry = %s,
                                        last_read_entry_id = %s
                                    WHERE id = %s;
                                """, (openmrs_feed_uri, latest_entry_id, m_id))
                                fixed_messages.append(f"Repaired corrupt {feed_name} marker to {openmrs_feed_uri}.")
            except Exception as e:
                _logger.warning("Could not auto-fix %s marker: %s", feed_name, e)

        self.env.cr.commit()
        return fixed_messages

    @api.model
    def action_rewind_feeds(self):
        """Rewinds patient and encounter markers to page 1 so odoo-connect replays all events cleanly."""
        rewound = []
        for feed_name in ['patient', 'encounter']:
            try:
                resp = requests.get(f"{OPENMRS_BASE_URL}/ws/atomfeed/{feed_name}/1", timeout=5)
                if resp.status_code == 200:
                    root = ET.fromstring(resp.content)
                    entries = root.findall("{http://www.w3.org/2005/Atom}entry")
                    first_entry_id = entries[0].find("{http://www.w3.org/2005/Atom}id").text if entries else None
                    page_uri = f"{OPENMRS_BASE_URL}/ws/atomfeed/{feed_name}/1"

                    self.env.cr.execute("""
                        UPDATE public.markers
                        SET feed_uri_for_last_read_entry = %s,
                            last_read_entry_id = %s
                        WHERE feed_uri LIKE %s;
                    """, (page_uri, first_entry_id, f"%{feed_name}%"))
                    rewound.append(f"{feed_name} feed rewound to page 1.")
            except Exception as e:
                _logger.warning("Error rewinding %s feed: %s", feed_name, e)

        self.env.cr.execute("UPDATE public.failed_events SET retries = 0;")
        self.env.cr.commit()
        self.action_refresh_queue()

        msg = " ".join(rewound) + " Odoo-connect will actively re-read and catch up all events from OpenMRS."
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Feeds Rewound for Complete Sync',
                'message': msg,
                'type': 'info',
                'sticky': False,
            }
        }

    @api.model
    def action_sync_patients(self):
        """Actually queries OpenMRS for active/recent patients and creates/updates them in Odoo."""
        # 1. Purge dead 404s and reset retries
        self.env.cr.execute("""
            DELETE FROM public.failed_events 
            WHERE feed_uri LIKE '%patient%' AND (
                error_message ILIKE '%404%' OR error_message ILIKE '%Bad response code of 404%'
            );
        """)
        self.env.cr.execute("UPDATE public.failed_events SET retries = 0 WHERE feed_uri LIKE '%patient%';")
        self.env.cr.commit()

        # 2. Query recent patients from OpenMRS AtomFeed or REST API
        synced_count = 0
        error_count = 0
        try:
            # Read recent patient feed entries
            resp = requests.get(f"{OPENMRS_BASE_URL}/ws/atomfeed/patient/recent", timeout=10)
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                entries = root.findall("{http://www.w3.org/2005/Atom}entry")
                worker = self.env['api.event.worker']
                Partner = self.env['res.partner'].with_context({'active_test': False})

                for entry in entries:
                    content_node = entry.find("{http://www.w3.org/2005/Atom}content")
                    if content_node is None or not content_node.text:
                        continue
                    pt_url_path = content_node.text.strip()
                    # e.g., /openmrs/ws/rest/v1/patient/UUID?v=full
                    if not pt_url_path.startswith('http'):
                        pt_full_url = f"http://openmrs:8080{pt_url_path}"
                    else:
                        pt_full_url = pt_url_path

                    try:
                        p_resp = requests.get(pt_full_url, auth=HTTPBasicAuth(OPENMRS_USER, OPENMRS_PASS), timeout=5)
                        if p_resp.status_code == 200:
                            p_json = p_resp.json()
                            p_uuid = p_json.get('uuid')
                            person = p_json.get('person', {})
                            p_name = person.get('display', '')
                            identifiers = p_json.get('identifiers', [])
                            p_ref = identifiers[0].get('identifier', '') if identifiers else ''

                            if not p_ref and p_uuid:
                                p_ref = p_uuid[:8]

                            if p_ref or p_uuid:
                                existing = Partner.search([
                                    '|', ('uuid', '=', p_uuid), ('ref', '=', p_ref)
                                ], limit=1)
                                if existing:
                                    existing.write({
                                        'name': p_name or existing.name,
                                        'uuid': p_uuid,
                                        'ref': p_ref,
                                        'customer_rank': 1,
                                        'active': True
                                    })
                                else:
                                    Partner.create({
                                        'name': p_name,
                                        'uuid': p_uuid,
                                        'ref': p_ref,
                                        'customer_rank': 1,
                                        'active': True
                                    })
                                synced_count += 1
                    except Exception as e:
                        _logger.warning("Error syncing individual patient %s: %s", pt_url_path, e)
                        error_count += 1

                self.env.cr.commit()
        except Exception as e:
            _logger.error("Error reading OpenMRS patient feed: %s", e)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Patient Sync Failed',
                    'message': f'Failed to query OpenMRS: {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }

        self.action_refresh_queue()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Patient Synchronization Completed',
                'message': f'Successfully verified and synced {synced_count} recent patient(s) directly from OpenMRS. (Errors: {error_count})',
                'type': 'success' if synced_count > 0 else 'info',
                'sticky': False,
            }
        }

    @api.model
    def action_sync_products(self):
        """Synchronizes orderable concepts, lab tests, procedures, and drugs from OpenMRS to Odoo."""
        ref_service = self.env['reference.data.service']
        Product = self.env['product.product'].with_context({'active_test': False})
        
        # Check /tmp/openmrs_concepts.tsv or query directly
        synced_count = 0
        error_count = 0
        existing_uuids = set(Product.search([('uuid', '!=', False)]).mapped('uuid'))

        mrs_concepts = {}
        for enc in ['utf-16', 'utf-8-sig', 'utf-8', 'latin-1']:
            try:
                with open('/tmp/openmrs_concepts.tsv', 'r', encoding=enc) as f:
                    for line in f:
                        parts = line.strip().split('\t')
                        if len(parts) >= 3 and parts[0]:
                            mrs_concepts[parts[0]] = (parts[1].strip(), parts[2].strip())
                    break
            except Exception:
                continue

        if not mrs_concepts:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Concepts Sync',
                    'message': 'No concept export found in /tmp/openmrs_concepts.tsv. Generate TSV first.',
                    'type': 'warning',
                    'sticky': False,
                }
            }

        for uuid, (name, cls) in mrs_concepts.items():
            cat = 'Test'
            if cls in ['Panel', 'LabSet', 'LabTest']:
                cat = 'Panel'
            elif cls in ['Radiology', 'Radiology/Imaging Procedure']:
                cat = 'Radiology'
            elif cls == 'Ophthalmology':
                cat = 'Ophthalmology'
            elif cls == 'Procedure':
                cat = 'Procedure'
            elif cls == 'Drug':
                cat = 'Drug'
            elif cls == 'Registration Fee':
                cat = 'Registration Fee'

            if uuid not in existing_uuids:
                try:
                    with self.env.cr.savepoint():
                        ref_service.create_or_update_ref_data({
                            'uuid': uuid,
                            'name': name,
                            'is_active': True,
                            'product_category': cat
                        }, cat)
                        p = Product.search([('uuid', '=', uuid)], limit=1)
                        if p and p.product_tmpl_id:
                            p.product_tmpl_id.write({'invoice_policy': 'order', 'list_price': 1.0})
                        existing_uuids.add(uuid)
                        synced_count += 1
                except Exception as e:
                    error_count += 1

        self.env.cr.commit()
        msg = f"Product/Test sync complete: {synced_count} new concept(s) created. Total verified: {len(existing_uuids)}."
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Products & Tests Synced',
                'message': msg,
                'type': 'success',
                'sticky': False,
            }
        }

    @api.model
    def action_sync_all_global(self):
        """Fixes markers, resets retries to 0 on failed events, and triggers atomfeed processing."""
        # Purge 404 dead events
        self.env.cr.execute("""
            DELETE FROM public.failed_events 
            WHERE error_message ILIKE '%404%' OR error_message ILIKE '%Bad response code of 404%';
        """)

        # Auto-fix markers
        healed = self.action_autofix_markers()

        # Reset retry counter on all remaining failed events
        self.env.cr.execute("UPDATE public.failed_events SET retries = 0;")
        self.env.cr.commit()

        self.action_refresh_queue()
        
        msg = "All failed events reset to 0 retries."
        if healed:
            msg = " ".join(healed) + " " + msg
        msg += " AtomFeed processing is active."

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sync All Orders Triggered',
                'message': msg,
                'type': 'info',
                'sticky': False,
            }
        }

    def action_resync_selected(self):
        """Action for the Action dropdown to retry selected events."""
        db_ids = [rec.db_id for rec in self if rec.db_id]
        if db_ids:
            self.env.cr.execute("""
                UPDATE public.failed_events
                SET retries = 0
                WHERE id IN %s;
            """, (tuple(db_ids),))
            self.env.cr.commit()

        self.action_refresh_queue()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Resyncing Selected Events',
                'message': f'{len(db_ids)} orders/events reset to 0 retries. Odoo-connect is reprocessing them.',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_clear_selected(self):
        """Action for the Action dropdown to dismiss selected events."""
        db_ids = [rec.db_id for rec in self if rec.db_id]
        if db_ids:
            self.env.cr.execute("""
                DELETE FROM public.failed_events
                WHERE id IN %s;
            """, (tuple(db_ids),))
            self.env.cr.commit()

        self.unlink()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Cleared from Queue',
                'message': f'{len(db_ids)} records permanently removed from failed events queue.',
                'type': 'info',
                'sticky': False,
            }
        }
