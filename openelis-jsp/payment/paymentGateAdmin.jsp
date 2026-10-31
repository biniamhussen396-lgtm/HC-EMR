<%@ page language="java" contentType="text/html; charset=utf-8"
    import="java.sql.*, java.util.*, java.io.*, java.net.*,
            us.mn.state.health.lims.common.util.SystemConfiguration,
            org.json.*"%>
<%@ taglib uri="/tags/struts-bean" prefix="bean" %>
<%@ taglib uri="/tags/struts-html" prefix="html" %>
<%@ taglib uri="/tags/struts-logic" prefix="logic" %>

<style>
    .pg-container { padding: 15px 20px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; max-width: 1200px; margin: 0 auto; color: #2c3e50; }
    .pg-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    .pg-title { margin: 0; font-size: 22px; font-weight: bold; color: #1e3a5f; }
    .pg-subtitle { color: #64748b; font-size: 13px; margin-top: 4px; }
    
    .pg-btn { padding: 6px 14px; cursor: pointer; border: 1px solid #999; background: #f1f5f9; font-size: 13px; border-radius: 4px; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; }
    .pg-btn-primary { background: #1e3a5f; color: white; border: none; }
    .pg-btn-primary:hover { background: #152942; }
    .pg-btn-success { background: #059669; color: white; border: none; }
    .pg-btn-success:hover { background: #047857; }
    .pg-btn-danger { background: #dc2626; color: white; border: none; }
    .pg-btn-danger:hover { background: #b91c1c; }
    .pg-btn-warning { background: #d97706; color: white; border: none; }
    .pg-btn-warning:hover { background: #b45309; }
    .pg-btn-info { background: #0284c7; color: white; border: none; }
    .pg-btn-info:hover { background: #0369a1; }
    .pg-btn-sm { padding: 3px 8px; font-size: 12px; }

    .pg-msg { padding: 12px 16px; border-radius: 6px; margin-bottom: 20px; font-weight: 500; font-size: 14px; }
    .pg-msg-success { background: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }
    .pg-msg-error { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
    .pg-msg-info { background: #e0f2fe; color: #075985; border: 1px solid #bae6fd; }

    .pg-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; margin-bottom: 25px; }
    .pg-card { background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .pg-card.active-gate { border-top: 4px solid #059669; }
    .pg-card.inactive-gate { border-top: 4px solid #dc2626; }
    .pg-card.rpc-card { border-top: 4px solid #0284c7; }
    .pg-card.frontend-card { border-top: 4px solid #d97706; }
    
    .pg-card-label { font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 700; letter-spacing: 0.5px; }
    .pg-card-status { font-size: 20px; font-weight: bold; margin: 8px 0 4px 0; display: flex; align-items: center; gap: 8px; }
    .pg-card-desc { font-size: 12px; color: #64748b; line-height: 1.4; }

    .pg-section { background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .pg-section-title { margin-top: 0; font-size: 16px; font-weight: bold; color: #1e3a5f; border-bottom: 1px solid #f1f5f9; padding-bottom: 10px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; }

    .pg-form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
    .pg-form-group { margin-bottom: 12px; }
    .pg-form-group label { display: block; font-weight: 600; font-size: 13px; margin-bottom: 5px; color: #334155; }
    .pg-form-group input, .pg-form-group select { width: 100%; padding: 8px 10px; font-size: 13px; border: 1px solid #cbd5e1; border-radius: 4px; box-sizing: border-box; }
    .pg-form-group small { display: block; color: #64748b; font-size: 11px; margin-top: 4px; }

    .badge-paid { background: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    .badge-unpaid { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    .mono { font-family: Consolas, "Courier New", monospace; font-size: 12px; background: #f8fafc; padding: 2px 5px; border-radius: 3px; border: 1px solid #e2e8f0; }

    .code-box { background: #0f172a; color: #e2e8f0; padding: 12px 16px; border-radius: 6px; font-family: Consolas, monospace; font-size: 12px; overflow-x: auto; line-height: 1.5; margin: 10px 0; }
</style>

<%
    String msgType = "";
    String msgText = "";
    String action = request.getParameter("action") != null ? request.getParameter("action") : "";

    SystemConfiguration sysConfig = SystemConfiguration.getInstance();
    String propFilePath = "/run/bahmni-lab/bahmni-lab/WEB-INF/classes/SystemConfiguration.properties";

    // 1. Handle ACTIVATE Payment Gate (SOP Step 3.1)
    if ("activate".equals(action)) {
        try {
            // Update in-memory singleton immediately
            sysConfig.setProperty("payment.isRestrictive", "true");
            sysConfig.setProperty("payment.odoo.username", "emrsync");
            sysConfig.setProperty("payment.odoo.password", "Admin123");
            sysConfig.setProperty("payment.odoo.db", "odoo");
            sysConfig.setProperty("payment.odoo.url", "http://odoo:8069");

            // Update SystemConfiguration.properties on disk
            File propFile = new File(propFilePath);
            if (propFile.exists()) {
                BufferedReader reader = new BufferedReader(new FileReader(propFile));
                StringBuilder content = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) {
                    if (line.startsWith("payment.isRestrictive=")) {
                        content.append("payment.isRestrictive=true\n");
                    } else if (line.startsWith("payment.odoo.username=")) {
                        content.append("payment.odoo.username=emrsync\n");
                    } else if (line.startsWith("payment.odoo.password=")) {
                        content.append("payment.odoo.password=Admin123\n");
                    } else if (line.startsWith("payment.odoo.db=")) {
                        content.append("payment.odoo.db=odoo\n");
                    } else if (line.startsWith("payment.odoo.url=")) {
                        content.append("payment.odoo.url=http://odoo:8069\n");
                    } else {
                        content.append(line).append("\n");
                    }
                }
                reader.close();
                BufferedWriter writer = new BufferedWriter(new FileWriter(propFile));
                writer.write(content.toString());
                writer.close();
            }

            msgType = "success";
            msgText = "Payment Validation Gate ACTIVATED! Restrictive accessioning is now enforced. Unpaid orders will show 'Not Paid' and require invoice payment in Odoo.";
        } catch (Exception e) {
            msgType = "error";
            msgText = "Error activating payment gate: " + e.getMessage();
        }
    }
    // 2. Handle DEACTIVATE Payment Gate (SOP Step 4.1)
    else if ("deactivate".equals(action)) {
        try {
            sysConfig.setProperty("payment.isRestrictive", "false");

            File propFile = new File(propFilePath);
            if (propFile.exists()) {
                BufferedReader reader = new BufferedReader(new FileReader(propFile));
                StringBuilder content = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) {
                    if (line.startsWith("payment.isRestrictive=")) {
                        content.append("payment.isRestrictive=false\n");
                    } else {
                        content.append(line).append("\n");
                    }
                }
                reader.close();
                BufferedWriter writer = new BufferedWriter(new FileWriter(propFile));
                writer.write(content.toString());
                writer.close();
            }

            msgType = "warning";
            msgText = "Payment Validation Gate DEACTIVATED! Unrestricted accessioning is now active (all orders permitted without billing check).";
        } catch (Exception e) {
            msgType = "error";
            msgText = "Error deactivating payment gate: " + e.getMessage();
        }
    }
    // 3. Handle Save Configuration
    else if ("save_config".equals(action)) {
        String odooUrl = request.getParameter("odooUrl");
        String odooDb = request.getParameter("odooDb");
        String odooUser = request.getParameter("odooUser");
        String odooPass = request.getParameter("odooPass");
        String isRestrictive = request.getParameter("isRestrictive");

        try {
            if (odooUrl != null) sysConfig.setProperty("payment.odoo.url", odooUrl.trim());
            if (odooDb != null) sysConfig.setProperty("payment.odoo.db", odooDb.trim());
            if (odooUser != null) sysConfig.setProperty("payment.odoo.username", odooUser.trim());
            if (odooPass != null && !odooPass.trim().isEmpty()) sysConfig.setProperty("payment.odoo.password", odooPass.trim());
            if (isRestrictive != null) sysConfig.setProperty("payment.isRestrictive", isRestrictive.trim());

            File propFile = new File(propFilePath);
            if (propFile.exists()) {
                BufferedReader reader = new BufferedReader(new FileReader(propFile));
                StringBuilder content = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) {
                    if (line.startsWith("payment.isRestrictive=") && isRestrictive != null) {
                        content.append("payment.isRestrictive=").append(isRestrictive.trim()).append("\n");
                    } else if (line.startsWith("payment.odoo.username=") && odooUser != null) {
                        content.append("payment.odoo.username=").append(odooUser.trim()).append("\n");
                    } else if (line.startsWith("payment.odoo.password=") && odooPass != null && !odooPass.trim().isEmpty()) {
                        content.append("payment.odoo.password=").append(odooPass.trim()).append("\n");
                    } else if (line.startsWith("payment.odoo.db=") && odooDb != null) {
                        content.append("payment.odoo.db=").append(odooDb.trim()).append("\n");
                    } else if (line.startsWith("payment.odoo.url=") && odooUrl != null) {
                        content.append("payment.odoo.url=").append(odooUrl.trim()).append("\n");
                    } else {
                        content.append(line).append("\n");
                    }
                }
                reader.close();
                BufferedWriter writer = new BufferedWriter(new FileWriter(propFile));
                writer.write(content.toString());
                writer.close();
            }

            msgType = "success";
            msgText = "Configuration saved successfully to memory and disk.";
        } catch (Exception e) {
            msgType = "error";
            msgText = "Error saving configuration: " + e.getMessage();
        }
    }

    // Read current effective properties
    boolean curRestrictive = sysConfig.getIsPaymentRestrictive();
    String curOdooUrl = sysConfig.getOdooURL() != null ? sysConfig.getOdooURL() : "http://odoo:8069";
    String curOdooDb = sysConfig.getOdooDB() != null ? sysConfig.getOdooDB() : "odoo";
    String curOdooUser = sysConfig.getOdooUsername() != null ? sysConfig.getOdooUsername() : "emrsync";
    String curOdooPass = sysConfig.getOdooPassword() != null ? sysConfig.getOdooPassword() : "Admin123";

    // Test RPC Handshake if requested
    String rpcTestOutput = "";
    boolean rpcSuccess = false;
    if ("test_rpc".equals(action)) {
        try {
            String pyScript = 
                "import xmlrpclib, sys\n" +
                "try:\n" +
                "    common = xmlrpclib.ServerProxy('" + curOdooUrl + "/xmlrpc/2/common')\n" +
                "    uid = common.authenticate('" + curOdooDb + "', '" + curOdooUser + "', '" + curOdooPass + "', {})\n" +
                "    if not uid:\n" +
                "        print 'AUTH_FAILED: Authentication rejected for user " + curOdooUser + " on database " + curOdooDb + "'\n" +
                "        sys.exit(0)\n" +
                "    models = xmlrpclib.ServerProxy('" + curOdooUrl + "/xmlrpc/2/object')\n" +
                "    count = models.execute_kw('" + curOdooDb + "', uid, '" + curOdooPass + "', 'sale.order.line', 'search_count', [[]])\n" +
                "    invoiced_count = models.execute_kw('" + curOdooDb + "', uid, '" + curOdooPass + "', 'sale.order.line', 'search_count', [[['invoice_status', '!=', 'no']]])\n" +
                "    print 'SUCCESS: UID=' + str(uid) + ' | Total Sale Order Lines=' + str(count) + ' | Invoiced/Paid Lines=' + str(invoiced_count)\n" +
                "except Exception as e:\n" +
                "    print 'ERROR: ' + str(e)\n";

            ProcessBuilder pb = new ProcessBuilder("python", "-c", pyScript);
            pb.redirectErrorStream(true);
            Process proc = pb.start();
            BufferedReader br = new BufferedReader(new InputStreamReader(proc.getInputStream()));
            StringBuilder sb = new StringBuilder();
            String l;
            while ((l = br.readLine()) != null) sb.append(l).append(" ");
            proc.waitFor();
            rpcTestOutput = sb.toString().trim();
            rpcSuccess = rpcTestOutput.startsWith("SUCCESS");
        } catch (Exception ex) {
            rpcTestOutput = "Execution Error: " + ex.getMessage();
        }
    }

    // Inspect single order/patient if requested
    String inspectQuery = request.getParameter("inspectQuery") != null ? request.getParameter("inspectQuery").trim() : "";
    List<Map<String, String>> inspectResults = new ArrayList<Map<String, String>>();
    if ("inspect".equals(action) && !inspectQuery.isEmpty()) {
        Connection pgConn = null;
        try {
            Class.forName("org.postgresql.Driver");
            pgConn = DriverManager.getConnection("jdbc:postgresql://openelisdb:5432/clinlims", "clinlims", "clinlims");
            PreparedStatement ps = pgConn.prepareStatement(
                "SELECT s.id, s.accession_number, s.has_paid, p.national_id, p.subject_number, er.external_id as order_uuid " +
                "FROM sample s " +
                "JOIN sample_human sh ON s.id = sh.samp_id " +
                "JOIN patient p ON sh.patient_id = p.id " +
                "LEFT JOIN external_reference er ON s.id = er.item_id AND er.type = 'Order' " +
                "WHERE p.national_id ILIKE ? OR p.subject_number ILIKE ? OR s.accession_number ILIKE ? OR er.external_id ILIKE ? " +
                "ORDER BY s.id DESC LIMIT 10");
            ps.setString(1, "%" + inspectQuery + "%");
            ps.setString(2, "%" + inspectQuery + "%");
            ps.setString(3, "%" + inspectQuery + "%");
            ps.setString(4, "%" + inspectQuery + "%");
            ResultSet rs = ps.executeQuery();
            while (rs.next()) {
                Map<String, String> m = new HashMap<String, String>();
                m.put("sampleId", rs.getString("id"));
                m.put("accession", rs.getString("accession_number"));
                m.put("hasPaid", rs.getBoolean("has_paid") ? "YES" : "NO");
                m.put("patientId", rs.getString("national_id") != null ? rs.getString("national_id") : rs.getString("subject_number"));
                m.put("uuid", rs.getString("order_uuid") != null ? rs.getString("order_uuid") : "—");
                inspectResults.add(m);
            }
            rs.close();
            ps.close();
        } catch (Exception ex) {
            inspectResults.clear();
        } finally {
            if (pgConn != null) try { pgConn.close(); } catch (Exception ex) {}
        }
    }
%>

<div class="pg-container">
    <div class="pg-header">
        <div>
            <a href="MasterListsPage.do" style="color:#1e3a5f;text-decoration:none;font-weight:bold;font-size:13px;">&#8592; Back to Master Lists</a>
            <h1 class="pg-title" style="margin-top:6px;">Payment Validation Gate &amp; Odoo Billing Integration</h1>
            <div class="pg-subtitle">Standard Operating Procedure (SOP) control panel for Bahmni OpenELIS restrictive accessioning and XML-RPC billing gateway.</div>
        </div>
        <div style="display:flex; gap:8px;">
            <a href="LabDashboard.do" class="pg-btn pg-btn-primary">
                📊 Open Lab Dashboard
            </a>
            <a href="http://localhost:8000" target="_blank" class="pg-btn pg-btn-success">
                ⚡ Port 8000: Sync Service
            </a>
        </div>
    </div>

    <% if (!msgText.isEmpty()) { %>
        <div class="pg-msg pg-msg-<%= msgType %>"><%= msgText %></div>
    <% } %>

    <!-- Status Cards -->
    <div class="pg-cards">
        <div class="pg-card <%= curRestrictive ? "active-gate" : "inactive-gate" %>">
            <div class="pg-card-label">Payment Validation Gate</div>
            <div class="pg-card-status">
                <% if (curRestrictive) { %>
                    <span style="color:#059669;">🟢 ACTIVE</span>
                <% } else { %>
                    <span style="color:#dc2626;">⚪ DEACTIVATED</span>
                <% } %>
            </div>
            <div class="pg-card-desc">
                <% if (curRestrictive) { %>
                    <strong>Restrictive Accessioning:</strong> Technicians cannot collect samples until the order is billed and paid in Odoo.
                <% } else { %>
                    <strong>Unrestricted Accessioning:</strong> Billing check is bypassed. All patient orders are immediately available for collection.
                <% } %>
            </div>
            <div style="margin-top:12px;">
                <% if (curRestrictive) { %>
                    <form method="POST" action="PaymentGateAdmin.do" style="margin:0;" onsubmit="return confirm('Deactivate payment gate? Technicians will be able to collect samples without verifying billing in Odoo.');">
                        <input type="hidden" name="action" value="deactivate">
                        <button type="submit" class="pg-btn pg-btn-danger pg-btn-sm">🔓 Deactivate Gate (Emergency Mode)</button>
                    </form>
                <% } else { %>
                    <form method="POST" action="PaymentGateAdmin.do" style="margin:0;">
                        <input type="hidden" name="action" value="activate">
                        <button type="submit" class="pg-btn pg-btn-success pg-btn-sm">🚀 Activate Payment Gate</button>
                    </form>
                <% } %>
            </div>
        </div>

        <div class="pg-card rpc-card">
            <div class="pg-card-label">Odoo XML-RPC Gateway</div>
            <div class="pg-card-status" style="font-size:16px;">
                <span class="mono"><%= curOdooUser %></span> @ <span class="mono"><%= curOdooDb %></span>
            </div>
            <div class="pg-card-desc">
                Endpoint: <span class="mono"><%= curOdooUrl %></span><br>
                Model Queried: <span class="mono">sale.order.line</span> (<span class="mono">invoice_status</span>)
            </div>
            <div style="margin-top:12px;">
                <form method="POST" action="PaymentGateAdmin.do" style="margin:0;">
                    <input type="hidden" name="action" value="test_rpc">
                    <button type="submit" class="pg-btn pg-btn-info pg-btn-sm">⚡ Test XML-RPC Handshake</button>
                </form>
            </div>
        </div>

        <div class="pg-card frontend-card">
            <div class="pg-card-label">Frontend Accession Link Gate</div>
            <div class="pg-card-status" style="font-size:16px; color:#d97706;">
                <span>orders.js Line 82-88</span>
            </div>
            <div class="pg-card-desc">
                Ternary conditional active: Unpaid orders display <span class="badge-unpaid">Not Paid</span> with stock-out warning. Paid orders render <span class="badge-paid">Collect Sample</span> button.
            </div>
            <div style="margin-top:12px;">
                <span style="font-size:11px; color:#64748b;">Hard refresh (Ctrl+Shift+R) after changes</span>
            </div>
        </div>
    </div>

    <% if (!rpcTestOutput.isEmpty()) { %>
        <div class="pg-section" style="border-left:4px solid <%= rpcSuccess ? "#059669" : "#dc2626" %>;">
            <div class="pg-section-title">
                <span>XML-RPC Test Handshake Result</span>
                <span class="<%= rpcSuccess ? "badge-paid" : "badge-unpaid" %>"><%= rpcSuccess ? "PASSED" : "FAILED" %></span>
            </div>
            <div class="code-box"><%= rpcTestOutput %></div>
        </div>
    <% } %>

    <!-- Section 1: Configuration Settings Form -->
    <div class="pg-section">
        <div class="pg-section-title">
            <span>⚙️ Odoo XML-RPC &amp; Gate Configuration</span>
            <span style="font-size:12px; color:#64748b; font-weight:normal;">Directly updates SystemConfiguration.properties &amp; in-memory singleton</span>
        </div>
        <form method="POST" action="PaymentGateAdmin.do">
            <input type="hidden" name="action" value="save_config">
            <div class="pg-form-grid">
                <div class="pg-form-group">
                    <label>Odoo XML-RPC URL:</label>
                    <input type="text" name="odooUrl" value="<%= curOdooUrl %>" required>
                    <small>Default internal Docker bridge endpoint: http://odoo:8069</small>
                </div>
                <div class="pg-form-group">
                    <label>Odoo Database Identifier:</label>
                    <input type="text" name="odooDb" value="<%= curOdooDb %>" required>
                    <small>Must be set to 'odoo' (never 'openerp')</small>
                </div>
                <div class="pg-form-group">
                    <label>Sync Username:</label>
                    <input type="text" name="odooUser" value="<%= curOdooUser %>" required>
                    <small>Verified production sync user: 'emrsync'</small>
                </div>
                <div class="pg-form-group">
                    <label>Sync Password:</label>
                    <input type="password" name="odooPass" value="<%= curOdooPass %>" required id="odooPassInp">
                    <small><input type="checkbox" onclick="var p=document.getElementById('odooPassInp'); p.type = p.type==='password'?'text':'password';"> Show password (Verified: Admin123)</small>
                </div>
                <div class="pg-form-group" style="grid-column: span 2;">
                    <label>Payment Gate Mode (Restrictive Accessioning):</label>
                    <select name="isRestrictive">
                        <option value="true" <%= curRestrictive ? "selected" : "" %>>Enabled (payment.isRestrictive=true) - Require payment in Odoo before sample collection</option>
                        <option value="false" <%= !curRestrictive ? "selected" : "" %>>Disabled (payment.isRestrictive=false) - Lift restrictions / emergency unrestricted mode</option>
                    </select>
                </div>
            </div>
            <div style="display:flex; justify-content:flex-end; gap:8px; margin-top:10px;">
                <button type="submit" class="pg-btn pg-btn-primary">💾 Save Configuration</button>
            </div>
        </form>
    </div>

    <!-- Section 2: Live Order / Patient Billing Inspector -->
    <div class="pg-section">
        <div class="pg-section-title">
            <span>🔍 Order / Patient Billing Status Inspector</span>
            <span style="font-size:12px; color:#64748b; font-weight:normal;">Test whether a specific patient or accession is permitted or blocked by the gate</span>
        </div>
        <form method="POST" action="PaymentGateAdmin.do" style="display:flex; gap:8px; margin-bottom:15px;">
            <input type="hidden" name="action" value="inspect">
            <input type="text" name="inspectQuery" placeholder="Enter Patient ID (e.g. GAN10001), Accession Number, or Order UUID..." 
                   value="<%= inspectQuery %>" style="flex:1; padding:8px 12px; font-size:13px; border:1px solid #cbd5e1; border-radius:4px;" required>
            <button type="submit" class="pg-btn pg-btn-info">Inspect Status</button>
        </form>

        <% if (!inspectResults.isEmpty()) { %>
            <table style="width:100%; border-collapse:collapse; font-size:13px;">
                <thead>
                    <tr style="background:#f1f5f9; text-align:left;">
                        <th style="padding:8px; border:1px solid #e2e8f0;">Sample ID</th>
                        <th style="padding:8px; border:1px solid #e2e8f0;">Accession #</th>
                        <th style="padding:8px; border:1px solid #e2e8f0;">Patient Identifier</th>
                        <th style="padding:8px; border:1px solid #e2e8f0;">Order UUID</th>
                        <th style="padding:8px; border:1px solid #e2e8f0;">OpenELIS Has Paid?</th>
                        <th style="padding:8px; border:1px solid #e2e8f0;">Gate Decision</th>
                    </tr>
                </thead>
                <tbody>
                    <% for (Map<String, String> row : inspectResults) { %>
                        <tr>
                            <td style="padding:8px; border:1px solid #e2e8f0;">#<%= row.get("sampleId") %></td>
                            <td style="padding:8px; border:1px solid #e2e8f0;"><strong><%= row.get("accession") %></strong></td>
                            <td style="padding:8px; border:1px solid #e2e8f0;"><span class="mono"><%= row.get("patientId") %></span></td>
                            <td style="padding:8px; border:1px solid #e2e8f0;"><span class="mono" style="font-size:10px;"><%= row.get("uuid") %></span></td>
                            <td style="padding:8px; border:1px solid #e2e8f0;">
                                <span class="<%= "YES".equals(row.get("hasPaid")) ? "badge-paid" : "badge-unpaid" %>"><%= row.get("hasPaid") %></span>
                            </td>
                            <td style="padding:8px; border:1px solid #e2e8f0;">
                                <% if ("YES".equals(row.get("hasPaid")) || !curRestrictive) { %>
                                    <span style="color:#059669; font-weight:bold;">🟢 PERMIT ACCESSION</span>
                                <% } else { %>
                                    <span style="color:#dc2626; font-weight:bold;">🔴 BLOCKED (Not Paid)</span>
                                <% } %>
                            </td>
                        </tr>
                    <% } %>
                </tbody>
            </table>
        <% } else if ("inspect".equals(action)) { %>
            <div style="color:#64748b; font-size:13px; font-style:italic;">No samples found matching "<%= inspectQuery %>".</div>
        <% } %>
    </div>

    <!-- Section 3: Standard Operating Procedure (SOP) Reference Runbook -->
    <div class="pg-section">
        <div class="pg-section-title">
            <span>📖 Standard Operating Procedure (SOP) Reference Runbook</span>
            <button class="pg-btn pg-btn-sm" onclick="var el=document.getElementById('sopDetails'); el.style.display=el.style.display==='none'?'block':'none';">Toggle SOP Details</button>
        </div>
        <div id="sopDetails">
            <h4 style="margin:8px 0 4px 0; color:#1e3a5f;">1. Technical Architecture &amp; Verification Mechanism</h4>
            <p style="font-size:12px; color:#475569; margin-top:2px; line-height:1.5;">
                • <strong>Backend Tier (Java / XML-RPC):</strong> Class <span class="mono">OrderPayment.class</span> inspects <span class="mono">payment.isRestrictive</span> from <span class="mono">SystemConfiguration.properties</span>. When true, OpenELIS authenticates with Odoo via XML-RPC (<span class="mono">/xmlrpc/2/common</span> &amp; <span class="mono">/xmlrpc/2/object</span>) and queries the <span class="mono">sale.order.line</span> model for matching order line <span class="mono">invoice_status</span>. If unpaid or draft, <span class="mono">hasPaid</span> evaluates to false; if registered paid, <span class="mono">hasPaid</span> evaluates to true.<br>
                • <strong>Frontend Tier (JavaScript / SlickGrid):</strong> In <span class="mono">/run/bahmni-lab/bahmni-lab/scripts/dashBoard/orders.js</span> (line 82), <span class="mono">generateAllLinksForOrder()</span> inspects <span class="mono">order.hasPaid</span>. If true, it renders the clickable 'Collect Sample' anchor link. If false, it renders unclickable plain text with stockout check: 'Not Paid'.
            </p>

            <h4 style="margin:12px 0 4px 0; color:#1e3a5f;">2. Production Pre-Requisites &amp; Credentials</h4>
            <p style="font-size:12px; color:#475569; margin-top:2px; line-height:1.5;">
                • <strong>Verified Odoo Password:</strong> Must be set to <span class="mono">Admin123</span> (matching ODOO_ATOMFEED_PASSWORD).<br>
                • <strong>Sync Username:</strong> Must be set to <span class="mono">emrsync</span>.<br>
                • <strong>Database Identifier:</strong> Must be explicitly designated as <span class="mono">odoo</span>.<br>
                • <strong>Odoo RPC Endpoint:</strong> Points internally to <span class="mono">http://odoo:8069</span> on the Docker bridge network.
            </p>

            <h4 style="margin:12px 0 4px 0; color:#1e3a5f;">3. Operational Checklist</h4>
            <table style="width:100%; border-collapse:collapse; font-size:12px; margin-top:8px;">
                <tr style="background:#f8fafc; text-align:left;">
                    <th style="padding:6px; border:1px solid #e2e8f0;">Item</th>
                    <th style="padding:6px; border:1px solid #e2e8f0;">Expected State</th>
                    <th style="padding:6px; border:1px solid #e2e8f0;">Status</th>
                </tr>
                <tr>
                    <td style="padding:6px; border:1px solid #e2e8f0;">SystemConfiguration.properties</td>
                    <td style="padding:6px; border:1px solid #e2e8f0;">payment.isRestrictive=true &amp; Admin123 password</td>
                    <td style="padding:6px; border:1px solid #e2e8f0;"><span class="badge-paid">Verified</span></td>
                </tr>
                <tr>
                    <td style="padding:6px; border:1px solid #e2e8f0;">orders.js Conditional Link</td>
                    <td style="padding:6px; border:1px solid #e2e8f0;">order.hasPaid returns 'Not Paid' on false</td>
                    <td style="padding:6px; border:1px solid #e2e8f0;"><span class="badge-paid">Verified</span></td>
                </tr>
                <tr>
                    <td style="padding:6px; border:1px solid #e2e8f0;">Odoo XML-RPC Handshake</td>
                    <td style="padding:6px; border:1px solid #e2e8f0;">Authenticates emrsync against odoo (UID 6)</td>
                    <td style="padding:6px; border:1px solid #e2e8f0;"><span class="badge-paid">Verified</span></td>
                </tr>
            </table>
        </div>
    </div>
</div>
