<%@ page language="java" contentType="text/html; charset=utf-8"
    import="java.sql.*, java.util.*, java.net.*, java.io.*, org.json.*"%>
<%@ taglib uri="/tags/struts-bean" prefix="bean" %>
<%@ taglib uri="/tags/struts-html" prefix="html" %>
<%@ taglib uri="/tags/struts-logic" prefix="logic" %>

<style>
    .harm-container { padding: 10px 15px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; }
    .harm-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
    .harm-title { margin: 0; color: #2c3e50; font-size: 20px; font-weight: bold; }
    .harm-subtitle { color: #666; font-size: 13px; margin-top: 4px; }
    
    .harm-stats { display: flex; gap: 12px; margin-bottom: 15px; flex-wrap: wrap; }
    .harm-card { flex: 1; min-width: 140px; background: white; border: 1px solid #ddd; border-radius: 6px; padding: 10px 14px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .harm-card-label { font-size: 11px; text-transform: uppercase; color: #777; font-weight: 600; letter-spacing: 0.5px; }
    .harm-card-val { font-size: 22px; font-weight: bold; margin-top: 4px; }
    
    .harm-card.border-total { border-top: 4px solid #486086; }
    .harm-card.border-matched { border-top: 4px solid #27ae60; }
    .harm-card.border-mismatch { border-top: 4px solid #f39c12; }
    .harm-card.border-missing { border-top: 4px solid #e74c3c; }
    .harm-card.border-allthree { border-top: 4px solid #0284c7; }
    
    .harm-card.border-total .harm-card-val { color: #486086; }
    .harm-card.border-matched .harm-card-val { color: #27ae60; }
    .harm-card.border-mismatch .harm-card-val { color: #f39c12; }
    .harm-card.border-missing .harm-card-val { color: #e74c3c; }
    .harm-card.border-allthree .harm-card-val { color: #0284c7; }

    .harm-toolbar { background: white; border: 1px solid #ddd; border-radius: 6px; padding: 10px 14px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; gap: 10px; flex-wrap: wrap; }
    .harm-search { flex: 1; min-width: 250px; padding: 6px 12px; border: 1px solid #ccc; border-radius: 4px; font-size: 13px; }
    
    .harm-btn-group { display: inline-flex; border-radius: 4px; overflow: hidden; border: 1px solid #ccc; }
    .harm-tab-btn { padding: 5px 12px; background: #f8f9fa; border: none; border-right: 1px solid #ccc; font-size: 12px; cursor: pointer; color: #444; font-weight: 500; }
    .harm-tab-btn:last-child { border-right: none; }
    .harm-tab-btn.active { background: #486086; color: white; font-weight: bold; }
    .harm-tab-btn:hover:not(.active) { background: #e9ecef; }
    
    .harm-btn { padding: 6px 14px; cursor: pointer; border: 1px solid #999; background: #f0f0f0; font-size: 13px; border-radius: 4px; font-weight: 500; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; }
    .harm-btn-primary { background: #486086; color: white; border: none; }
    .harm-btn-primary:hover { background: #3a4f6f; }
    .harm-btn-success { background: #27ae60; color: white; border: none; }
    .harm-btn-success:hover { background: #219653; }
    .harm-btn-danger { background: #e74c3c; color: white; border: none; }
    .harm-btn-danger:hover { background: #c0392b; }
    .harm-btn-warning { background: #f39c12; color: white; border: none; }
    .harm-btn-sm { padding: 3px 8px; font-size: 11px; }

    .harm-table-card { background: white; border: 1px solid #ddd; border-radius: 6px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
    .harm-table { width: 100%; border-collapse: collapse; }
    .harm-table th { background: #486086; color: white; padding: 8px 8px; font-size: 12px; text-align: left; position: sticky; top: 0; }
    .harm-table td { padding: 7px 8px; border-bottom: 1px solid #eee; font-size: 12px; vertical-align: middle; }
    .harm-table tr:hover { background: #f1f6fa; }
    .harm-table-container { max-height: 600px; overflow-y: auto; }

    .badge-matched { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    .badge-mismatch { background: #fff3cd; color: #856404; border: 1px solid #ffeeba; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    .badge-missing { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    .badge-unlinked { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    
    .type-pill-test { background: #e8f4fd; color: #1e88e5; border: 1px solid #bbdefb; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    .type-pill-panel { background: #f3e5f5; color: #8e24aa; border: 1px solid #e1bee7; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    
    .mono { font-family: Consolas, monospace; font-size: 11px; color: #555; }
    .footer-bar { padding: 8px 12px; background: #fafafa; border-top: 1px solid #eee; display: flex; justify-content: space-between; font-size: 12px; color: #666; }
</style>

<div class="harm-container">
    <div style="margin-bottom:12px;">
        <a href="MasterListsPage.do" style="color:#486086;text-decoration:none;font-weight:bold;font-size:14px;">&#8592; Back to Master Lists</a>
    </div>

    <!-- Header -->
    <div class="harm-header">
        <div>
            <h2 class="harm-title">OpenMRS, OpenELIS &amp; Odoo Lab Harmonization</h2>
            <div class="harm-subtitle">Compare and synchronize laboratory tests and panels across OpenMRS, OpenELIS, and Odoo; purge unwanted dummy tests from all 3 systems.</div>
        </div>
        <div style="display:flex; gap:8px;">
            <button class="harm-btn harm-btn-primary" onclick="syncAll(this)">
                🔄 Sync All to OpenELIS
            </button>
            <button class="harm-btn harm-btn-danger" id="btnDeleteSelected" onclick="deleteSelected()" disabled>
                🗑️ Delete Selected
            </button>
            <a href="http://localhost:8000/harmonization" target="_blank" class="harm-btn harm-btn-success">
                ⚡ Port 8000: Full Dashboard
            </a>
            <button class="harm-btn" onclick="loadComparisonData()">
                ↻ Refresh
            </button>
        </div>
    </div>

    <!-- Summary Metrics Cards -->
    <div class="harm-stats">
        <div class="harm-card border-total">
            <div class="harm-card-label">Total OpenMRS</div>
            <div class="harm-card-val" id="statTotal">--</div>
        </div>
        <div class="harm-card border-matched">
            <div class="harm-card-label">Matched in OpenELIS</div>
            <div class="harm-card-val" id="statMatched">--</div>
        </div>
        <div class="harm-card border-mismatch">
            <div class="harm-card-label">Name Differences</div>
            <div class="harm-card-val" id="statMismatch">--</div>
        </div>
        <div class="harm-card border-missing">
            <div class="harm-card-label">Missing in OpenELIS</div>
            <div class="harm-card-val" id="statMissing">--</div>
        </div>
        <div class="harm-card border-allthree">
            <div class="harm-card-label">Synced in All 3</div>
            <div class="harm-card-val" id="statAllThree">--</div>
        </div>
    </div>

    <!-- Toolbar: Search and Filter Tabs -->
    <div class="harm-toolbar">
        <input type="text" id="harmSearch" class="harm-search" placeholder="🔍 Search test/panel name, UUID, ID in OpenMRS, OpenELIS, Odoo..." oninput="filterRows()">
        
        <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
            <div class="harm-btn-group">
                <button type="button" class="harm-tab-btn filter-btn active" data-filter="ALL" onclick="setFilter('ALL', this)">All</button>
                <button type="button" class="harm-tab-btn filter-btn" data-filter="MISSING" onclick="setFilter('MISSING', this)">🔴 Missing (<span id="btnMissingCount">0</span>)</button>
                <button type="button" class="harm-tab-btn filter-btn" data-filter="MISMATCH" onclick="setFilter('MISMATCH', this)">🟡 Name Diff (<span id="btnMismatchCount">0</span>)</button>
                <button type="button" class="harm-tab-btn filter-btn" data-filter="MATCHED" onclick="setFilter('MATCHED', this)">🟢 Matched</button>
                <button type="button" class="harm-tab-btn filter-btn" data-filter="MISSING_ODOO" onclick="setFilter('MISSING_ODOO', this)">🛒 Missing in Odoo</button>
            </div>

            <div class="harm-btn-group">
                <button type="button" class="harm-tab-btn type-btn active" data-type="ALL" onclick="setType('ALL', this)">All Types</button>
                <button type="button" class="harm-tab-btn type-btn" data-type="Test" onclick="setType('Test', this)">🧪 Tests</button>
                <button type="button" class="harm-tab-btn type-btn" data-type="Panel" onclick="setType('Panel', this)">📋 Panels</button>
            </div>
        </div>
    </div>

    <!-- Table -->
    <div class="harm-table-card">
        <div class="harm-table-container">
            <table class="harm-table" id="harmTable">
                <thead>
                    <tr>
                        <th style="width:30px; text-align:center;"><input type="checkbox" id="selectAllCheckbox" onchange="toggleSelectAll(this)"></th>
                        <th style="width:40px;">#</th>
                        <th style="width:75px;">Type</th>
                        <th>OpenMRS Concept Name</th>
                        <th>OpenMRS Concept UUID</th>
                        <th>OpenELIS Name &amp; ID</th>
                        <th>Odoo Product Name &amp; ID</th>
                        <th style="width:130px;">Status</th>
                        <th style="width:160px; text-align:center;">Actions</th>
                    </tr>
                </thead>
                <tbody id="harmTbody">
                    <tr>
                        <td colspan="9" style="text-align:center; padding:30px; color:#666;">
                            Loading comparison data...
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div class="footer-bar">
            <span id="footerText">Showing 0 items</span>
            <span>Synchronized across OpenMRS &bull; OpenELIS &bull; Odoo</span>
        </div>
    </div>
</div>

<script>
    var allItems = [];
    var currentFilter = 'ALL';
    var currentType = 'ALL';
    var selectedUuids = {};
    var apiBaseUrl = window.location.protocol + '//' + window.location.hostname + ':8000';

    function loadComparisonData() {
        var tbody = document.getElementById('harmTbody');
        tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; padding:30px; color:#666;">Loading comparison data across OpenMRS, OpenELIS & Odoo...</td></tr>';
        selectedUuids = {};
        updateDeleteSelectedBtn();

        fetch(apiBaseUrl + '/api/harmonization/comparison')
            .then(function(res) {
                if (!res.ok) throw new Error('Sync service returned status ' + res.status);
                return res.json();
            })
            .then(function(data) {
                var s = data.summary || {};
                document.getElementById('statTotal').innerText = s.total_openmrs || 0;
                document.getElementById('statMatched').innerText = s.matched || 0;
                document.getElementById('statMismatch').innerText = s.name_mismatch || 0;
                document.getElementById('statMissing').innerText = s.missing_in_openelis || 0;
                document.getElementById('statAllThree').innerText = s.matched_all_three || 0;
                document.getElementById('btnMissingCount').innerText = s.missing_in_openelis || 0;
                document.getElementById('btnMismatchCount').innerText = s.name_mismatch || 0;

                allItems = data.items || [];
                filterRows();
            })
            .catch(function(err) {
                tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; padding:30px; color:#c0392b;">' +
                    '<strong>Error connecting to sync service:</strong> ' + err.message + '<br>' +
                    '<small>Make sure the result sync service is running on port 8000.</small>' +
                    '</td></tr>';
            });
    }

    function setFilter(f, btn) {
        currentFilter = f;
        var btns = document.querySelectorAll('.filter-btn');
        for (var i = 0; i < btns.length; i++) btns[i].classList.remove('active');
        btn.classList.add('active');
        filterRows();
    }

    function setType(t, btn) {
        currentType = t;
        var btns = document.querySelectorAll('.type-btn');
        for (var i = 0; i < btns.length; i++) btns[i].classList.remove('active');
        btn.classList.add('active');
        filterRows();
    }

    function filterRows() {
        var q = (document.getElementById('harmSearch').value || '').toLowerCase().trim();
        var tbody = document.getElementById('harmTbody');

        var filtered = allItems.filter(function(item) {
            if (currentFilter === 'MISSING' && item.status !== 'MISSING_IN_OPENELIS') return false;
            if (currentFilter === 'MISMATCH' && item.status !== 'NAME_MISMATCH') return false;
            if (currentFilter === 'MATCHED' && item.status !== 'MATCHED') return false;
            if (currentFilter === 'MISSING_ODOO' && item.odoo_name) return false;

            if (currentType !== 'ALL' && item.type !== currentType) return false;

            if (q) {
                var omrs = (item.openmrs_name || '').toLowerCase();
                var elis = (item.openelis_name || '').toLowerCase();
                var odoo = (item.odoo_name || '').toLowerCase();
                var u = (item.uuid || '').toLowerCase();
                var elisId = String(item.openelis_id || '');
                var odooId = String(item.odoo_id || '');
                if (omrs.indexOf(q) === -1 && elis.indexOf(q) === -1 && odoo.indexOf(q) === -1 &&
                    u.indexOf(q) === -1 && elisId.indexOf(q) === -1 && odooId.indexOf(q) === -1) {
                    return false;
                }
            }
            return true;
        });

        if (filtered.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; padding:30px; color:#888;">No matching tests or panels found.</td></tr>';
            document.getElementById('footerText').innerText = 'Showing 0 of ' + allItems.length + ' items';
            return;
        }

        var html = '';
        for (var i = 0; i < filtered.length; i++) {
            var item = filtered[i];
            var badgeClass = 'badge-matched';
            if (item.status === 'MISSING_IN_OPENELIS') badgeClass = 'badge-missing';
            else if (item.status === 'NAME_MISMATCH') badgeClass = 'badge-mismatch';
            else if (item.status === 'UNLINKED_MATCH') badgeClass = 'badge-unlinked';

            var typePill = item.type === 'Panel' 
                ? '<span class="type-pill-panel">📋 Panel' + (item.member_count ? ' (' + item.member_count + ')' : '') + '</span>'
                : '<span class="type-pill-test">🧪 Test</span>';

            var elisDisplay = item.openelis_name 
                ? item.openelis_name + ' <span style="background:#eef; padding:1px 5px; border-radius:3px; font-weight:bold; font-size:10px;">#' + item.openelis_id + '</span>'
                : '<span style="color:#c0392b; font-style:italic;">— Not in OpenELIS —</span>';

            var odooDisplay = item.odoo_name 
                ? item.odoo_name + ' <span style="background:#eef; padding:1px 5px; border-radius:3px; font-weight:bold; font-size:10px;">#' + item.odoo_id + '</span>'
                : '<span style="color:#888; font-style:italic;">— Not in Odoo —</span>';

            var isChecked = selectedUuids[item.uuid] ? 'checked' : '';

            var actions = '<div style="display:flex; justify-content:center; gap:4px;">';
            if (item.status === 'MISSING_IN_OPENELIS') {
                actions += '<button class="harm-btn harm-btn-sm" style="border-color:#486086; color:#486086;" onclick="syncSingle(\'' + item.uuid + '\', \'' + item.type + '\', \'create\', this)">Sync</button>';
            } else if (item.status === 'NAME_MISMATCH') {
                actions += '<button class="harm-btn harm-btn-warning harm-btn-sm" onclick="syncSingle(\'' + item.uuid + '\', \'' + item.type + '\', \'fix_name\', this)">Fix Name</button>';
            }
            actions += '<button class="harm-btn harm-btn-danger harm-btn-sm" title="Delete from OpenMRS, OpenELIS & Odoo" onclick="deleteSingle(\'' + item.uuid + '\', \'' + item.openmrs_name.replace(/'/g, "\\'") + '\', \'' + item.type + '\')">🗑️ Delete</button>';
            actions += '</div>';

            html += '<tr>' +
                '<td style="text-align:center;"><input type="checkbox" class="row-checkbox" data-uuid="' + item.uuid + '" ' + isChecked + ' onchange="toggleSelectRow(\'' + item.uuid + '\', this)"></td>' +
                '<td style="color:#888;">' + (i + 1) + '</td>' +
                '<td>' + typePill + '</td>' +
                '<td><strong>' + item.openmrs_name + '</strong></td>' +
                '<td><span class="mono">' + item.uuid + '</span></td>' +
                '<td>' + elisDisplay + '</td>' +
                '<td>' + odooDisplay + '</td>' +
                '<td><span class="' + badgeClass + '">' + item.status_label + '</span></td>' +
                '<td style="text-align:center;">' + actions + '</td>' +
                '</tr>';
        }

        tbody.innerHTML = html;
        document.getElementById('footerText').innerText = 'Showing ' + filtered.length + ' of ' + allItems.length + ' items';
    }

    function toggleSelectRow(uuid, cb) {
        if (cb.checked) selectedUuids[uuid] = true;
        else delete selectedUuids[uuid];
        updateDeleteSelectedBtn();
    }

    function toggleSelectAll(masterCb) {
        var cbs = document.querySelectorAll('.row-checkbox');
        for (var i = 0; i < cbs.length; i++) {
            cbs[i].checked = masterCb.checked;
            var u = cbs[i].getAttribute('data-uuid');
            if (masterCb.checked) selectedUuids[u] = true;
            else delete selectedUuids[u];
        }
        updateDeleteSelectedBtn();
    }

    function updateDeleteSelectedBtn() {
        var btn = document.getElementById('btnDeleteSelected');
        var keys = Object.keys(selectedUuids);
        btn.disabled = keys.length === 0;
        btn.innerHTML = '🗑️ Delete Selected (' + keys.length + ')';
    }

    function deleteSingle(uuid, name, type) {
        if (!confirm('Are you sure you want to permanently delete or retire "' + name + '" across:\n• OpenMRS\n• OpenELIS\n• Odoo?')) {
            return;
        }

        fetch(apiBaseUrl + '/api/harmonization/delete-item', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ uuid: uuid, type: type })
        })
        .then(function(res) { return res.json(); })
        .then(function(res) {
            if (res.success) {
                alert('Deleted: ' + (res.message || 'Successfully deleted across OpenMRS, OpenELIS & Odoo'));
                loadComparisonData();
            } else {
                alert('Delete Error: ' + (res.error || 'Failed to delete'));
            }
        })
        .catch(function(err) {
            alert('Request error: ' + err.message);
        });
    }

    function deleteSelected() {
        var keys = Object.keys(selectedUuids);
        if (keys.length === 0) return;

        if (!confirm('Are you sure you want to delete these ' + keys.length + ' unwanted tests/panels across OpenMRS, OpenELIS, and Odoo?')) {
            return;
        }

        var btn = document.getElementById('btnDeleteSelected');
        btn.disabled = true;
        btn.innerText = 'Deleting...';

        fetch(apiBaseUrl + '/api/harmonization/delete-batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ uuids: keys })
        })
        .then(function(res) { return res.json(); })
        .then(function(res) {
            if (res.success) {
                alert('Batch deletion completed!\nSuccessfully processed ' + res.deleted_count + ' items across OpenMRS, OpenELIS & Odoo.');
                loadComparisonData();
            } else {
                alert('Error: ' + (res.error || 'Failed batch delete'));
                btn.disabled = false;
            }
        })
        .catch(function(err) {
            alert('Request error: ' + err.message);
            btn.disabled = false;
        });
    }

    function syncSingle(uuid, type, action, btn) {
        btn.disabled = true;
        var old = btn.innerText;
        btn.innerText = '...';

        fetch(apiBaseUrl + '/api/harmonization/sync-single', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ uuid: uuid, type: type, action: action })
        })
        .then(function(res) { return res.json(); })
        .then(function(res) {
            if (res.success) {
                alert(res.message || 'Synced successfully!');
                loadComparisonData();
            } else {
                alert('Error: ' + (res.error || 'Failed to sync'));
                btn.disabled = false;
                btn.innerText = old;
            }
        })
        .catch(function(err) {
            alert('Request error: ' + err.message);
            btn.disabled = false;
            btn.innerText = old;
        });
    }

    function syncAll(btn) {
        if (!confirm('Are you sure you want to sync all tests and panels from OpenMRS into OpenELIS? Any missing tests/panels will be created and name mismatches updated.')) {
            return;
        }

        btn.disabled = true;
        var old = btn.innerText;
        btn.innerText = 'Syncing all...';

        fetch(apiBaseUrl + '/api/harmonization/sync-all', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sync_missing: true, fix_names: true, link_unlinked: true })
        })
        .then(function(res) { return res.json(); })
        .then(function(res) {
            if (res.success) {
                var r = res.results || {};
                alert('Harmonization completed successfully!\n' +
                      'Created in OpenELIS: ' + (r.created || 0) + '\n' +
                      'Updated Names: ' + (r.updated_names || 0) + '\n' +
                      'Linked UUIDs: ' + (r.linked || 0));
                loadComparisonData();
            } else {
                alert('Error: ' + (res.error || 'Full sync failed'));
            }
        })
        .catch(function(err) {
            alert('Request error: ' + err.message);
        })
        .finally(function() {
            btn.disabled = false;
            btn.innerText = old;
        });
    }

    document.addEventListener('DOMContentLoaded', function() {
        loadComparisonData();
    });
</script>
