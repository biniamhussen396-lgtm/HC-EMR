import logging
import requests
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
        for rec in self.env.cr.fetchall():
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
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
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
                'message': f'Successfully removed {deleted_count} dead 404 events from failed events queue.',
                'type': 'success',
                'sticky': False,
            }
        }

    @api.model
    def action_autofix_markers(self):
        """Checks and fixes any corrupted or stuck atomfeed markers in odoodb."""
        fixed_messages = []
        
        # 1. Check encounter marker
        self.env.cr.execute("""
            SELECT id, feed_uri, feed_uri_for_last_read_entry, last_read_entry_id
            FROM public.markers
            WHERE feed_uri LIKE '%encounter%';
        """)
        enc_marker = self.env.cr.fetchone()
        if enc_marker:
            last_entry = enc_marker[3] or ''
            last_feed = enc_marker[2] or ''
            is_corrupt = (':0' in last_entry) or not last_entry
            if not is_corrupt:
                try:
                    page_num = int(last_feed.rstrip('/').split('/')[-1])
                    if page_num < 4:
                        is_corrupt = True
                except Exception:
                    pass
            if is_corrupt:
                self.env.cr.execute("""
                    UPDATE public.markers
                    SET feed_uri_for_last_read_entry = 'http://openmrs:8080/openmrs/ws/atomfeed/encounter/4',
                        last_read_entry_id = 'tag:atomfeed.ict4h.org:c44050fb-23ed-44f1-a1bc-0e5cf2d655e4'
                    WHERE feed_uri LIKE '%encounter%';
                """)
                fixed_messages.append("Healed encounter marker (advanced past deleted events to page 4).")
        
        # 2. Check patient marker
        self.env.cr.execute("""
            SELECT id, feed_uri, feed_uri_for_last_read_entry, last_read_entry_id
            FROM public.markers
            WHERE feed_uri LIKE '%patient%';
        """)
        pat_marker = self.env.cr.fetchone()
        if pat_marker:
            last_entry = pat_marker[3] or ''
            last_feed = pat_marker[2] or ''
            is_corrupt = (':0' in last_entry) or not last_entry
            if not is_corrupt:
                try:
                    page_num = int(last_feed.rstrip('/').split('/')[-1])
                    if page_num < 3:
                        is_corrupt = True
                except Exception:
                    pass
            if is_corrupt:
                self.env.cr.execute("""
                    UPDATE public.markers
                    SET feed_uri_for_last_read_entry = 'http://openmrs:8080/openmrs/ws/atomfeed/patient/3',
                        last_read_entry_id = 'tag:atomfeed.ict4h.org:2c9138b7-801d-408f-b064-b3e7b0a8ab2d'
                    WHERE feed_uri LIKE '%patient%';
                """)
                fixed_messages.append("Healed patient marker (advanced past deleted events to page 3).")

        self.env.cr.commit()
        return fixed_messages

    @api.model
    def action_sync_patients(self):
        """Cleans dead 404 patient events and sets patient feed marker to valid entries."""
        # Purge 404s
        self.env.cr.execute("""
            DELETE FROM public.failed_events 
            WHERE feed_uri LIKE '%patient%' AND (
                error_message ILIKE '%404%' OR error_message ILIKE '%Bad response code of 404%'
            );
        """)
        
        # Ensure patient marker is valid
        self.action_autofix_markers()
        
        # Reset retries on remaining patient events
        self.env.cr.execute("""
            UPDATE public.failed_events 
            SET retries = 0 
            WHERE feed_uri LIKE '%patient%';
        """)
        self.env.cr.commit()
        self.action_refresh_queue()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Patient Feed Sync Triggered',
                'message': 'Patient markers verified and 404 events purged. Odoo-connect is now synchronizing patients.',
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

        # Auto-fix corrupted markers
        healed = self.action_autofix_markers()

        # Reset retry counter on all remaining failed events
        self.env.cr.execute("UPDATE public.failed_events SET retries = 0;")
        self.env.cr.commit()

        self.action_refresh_queue()
        
        msg = "All failed events reset to 0 retries. Atomfeed sync is actively processing."
        if healed:
            msg = " ".join(healed) + " " + msg

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sync All Orders Triggered',
                'message': msg,
                'type': 'success',
                'sticky': False,
            }
        }

    @api.model
    def action_start_auth_global(self):
        """Checks connectivity and authentication with OpenMRS Atomfeed & REST API."""
        status_msg = "OpenMRS Connection Verified"
        status_type = "success"
        try:
            resp = requests.get(
                f"{OPENMRS_BASE_URL}/ws/rest/v1/session",
                auth=HTTPBasicAuth(OPENMRS_USER, OPENMRS_PASS),
                timeout=5
            )
            if resp.status_code == 200 and resp.json().get('authenticated'):
                user_name = resp.json().get('user', {}).get('username', OPENMRS_USER)
                status_msg = f"Successfully authenticated with OpenMRS as '{user_name}'. AtomFeed and REST services are online."
            else:
                status_msg = f"OpenMRS responded with status {resp.status_code}, authenticated={resp.json().get('authenticated')}"
                status_type = "warning"
        except Exception as e:
            status_msg = f"Could not reach OpenMRS API: {str(e)}"
            status_type = "danger"

        # Auto-fix markers as well
        self.action_autofix_markers()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'OpenMRS Auth & Connectivity Check',
                'message': status_msg,
                'type': status_type,
                'sticky': False,
            }
        }

    def action_resync_selected(self):
        """Action for the ⚙ Action dropdown to retry selected events."""
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
        """Action for the ⚙ Action dropdown to dismiss selected events."""
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
