<%@ page language="java" contentType="text/html; charset=utf-8"
    import="java.sql.*, java.util.*, java.text.DecimalFormat"%>
<%@ taglib uri="/tags/struts-bean" prefix="bean" %>
<%@ taglib uri="/tags/struts-html" prefix="html" %>
<%@ taglib uri="/tags/struts-logic" prefix="logic" %>

<html:html>
<head>
<title>Analyzer Configuration</title>
<style>
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
    th { background: #486086; color: white; }
    .required { color: red; }
    .btn { padding: 6px 16px; cursor: pointer; border: 1px solid #999; background: #f0f0f0; margin: 2px; }
    .btn-primary { background: #486086; color: white; border: none; }
    .btn-danger { background: #c0392b; color: white; border: none; }
    .btn-success { background: #27ae60; color: white; border: none; }
    .success { color: green; font-weight: bold; }
    .error { color: red; font-weight: bold; }
    .label { font-weight: bold; width: 200px; }
    input[type=text], select { width: 300px; padding: 4px; }
    .setup-box { background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 20px; margin: 15px 0; }
    .setup-box h3 { margin-top: 0; color: #486086; }
    .step-num { display: inline-block; width: 28px; height: 28px; background: #486086; color: white; border-radius: 50%; text-align: center; line-height: 28px; font-weight: bold; margin-right: 8px; }
    .step { margin: 12px 0; padding-left: 40px; position: relative; }
    .step p { margin: 4px 0; }
    code { background: #e9ecef; padding: 2px 6px; border-radius: 3px; font-size: 13px; }
    pre { background: #2d2d2d; color: #f8f8f2; padding: 12px; border-radius: 4px; overflow-x: auto; font-size: 13px; }
    .flow-diagram { background: white; border: 2px solid #486086; border-radius: 6px; padding: 15px; margin: 15px 0; text-align: center; font-family: monospace; font-size: 14px; }
    .flow-box { display: inline-block; border: 2px solid #486086; border-radius: 6px; padding: 8px 14px; margin: 4px; background: #e8eef5; }
    .flow-arrow { display: inline-block; font-size: 20px; margin: 0 6px; vertical-align: middle; }
    .ref-table th { font-size: 13px; }
    .ref-table td { font-size: 13px; }
    #dbTable th { font-size: 13px; white-space: nowrap; }
    #dbTable td { font-size: 13px; }
    #dbTable { font-size: 13px; }
    #dbCount { color: #486086; font-size: 14px; }
    .tabs { display: flex; border-bottom: 2px solid #486086; margin-bottom: 0; }
    .tab { padding: 10px 20px; cursor: pointer; background: #e8eef5; border: 1px solid #ccc; border-bottom: none; margin-right: 2px; border-radius: 4px 4px 0 0; }
    .tab.active { background: #486086; color: white; }
    .tab-content { display: none; padding: 15px 0; }
    .tab-content.active { display: block; }
</style>
</head>
<body>
<div style="background:#486086;color:white;padding:10px 20px;font-size:20px;display:flex;align-items:center;justify-content:space-between;">
    <span>Analyzer Configuration - Manage Results Dropdown</span>
    <a href="MasterListsPage.do" style="color:white;text-decoration:none;background:#2c3e50;padding:6px 16px;border-radius:4px;font-size:14px;">&#8592; Back to Master Lists</a>
</div>
<div style="padding:20px;">

<div class="tabs">
    <div class="tab active" onclick="showTab('setup')">Complete Setup Guide</div>
    <div class="tab" onclick="showTab('manage')">Results Dropdown</div>
    <div class="tab" onclick="showTab('analyzerdb')">Analyzer Database</div>
    <div class="tab" onclick="showTab('testmap')">Test Name Mapping</div>
    <div class="tab" onclick="showTab('tcp')">TCP/IP Bridge</div>
</div>

<!-- TAB 1: Setup Guide -->
<div id="tab-setup" class="tab-content active">
<h2>Complete Analyzer Setup Guide</h2>

<div class="flow-diagram">
    <strong>Architecture Flow:</strong><br/><br/>
    <div class="flow-box">Physical Analyzer<br/><small>Mindray BC 5150</small></div>
    <span class="flow-arrow">&rarr;</span>
    <div class="flow-box">TCP/IP Bridge<br/><small>Python Script</small></div>
    <span class="flow-arrow">&rarr;</span>
    <div class="flow-box">OpenELIS<br/><small>/addAnalyzerData</small></div>
    <span class="flow-arrow">&rarr;</span>
    <div class="flow-box">Results Queue<br/><small>Results &rarr; Analyzer</small></div>
    <span class="flow-arrow">&rarr;</span>
    <div class="flow-box">Patient Record<br/><small>Validated Results</small></div>
</div>

<div class="setup-box">
<h3>Step 1: Register Analyzer in OpenELIS</h3>
<div class="step">
    <p>The analyzer must be registered in the <code>analyzer</code> database table.</p>
    <p>This is done automatically when you add test name mappings via <strong>Administration &rarr; Analyzer Test Names</strong>.</p>
    <p>If your analyzer is not listed, contact the system administrator to add it to the database.</p>
</div>
</div>

<div class="setup-box">
<h3>Step 2: Map Analyzer Test Names to OpenELIS Tests</h3>
<div class="step">
    <p>Go to <strong>Administration &rarr; Analyzer Test Names</strong> and click <strong>Add</strong>.</p>
    <p>For each test the analyzer outputs, create a mapping:</p>
    <table class="ref-table" style="width:auto; margin:10px 0;">
        <tr><th>Field</th><th>Description</th><th>Example</th></tr>
        <tr><td>Analyzer</td><td>Select your analyzer</td><td>Mindray BC 5150</td></tr>
        <tr><td>Analyzer Test Name</td><td>Exact name from analyzer (case-sensitive)</td><td><code>WBC</code>, <code>RBC</code>, <code>HGB</code></td></tr>
        <tr><td>Actual Test Name</td><td>Corresponding OpenELIS test</td><td>White Blood Cell Count</td></tr>
    </table>
    <p><strong>Mindray BC 5150 tests:</strong> WBC, RBC, HGB, HCT, MCV, MCH, MCHC, PLT, LYM%, LYM#, MON%, MON#, NEU%, NEU#, EOS%, EOS#, BAS%, BAS#, RDW-CV, RDW-SD, MPV, PDW, P-LCR, PLCC</p>
</div>
</div>

<div class="setup-box">
<h3>Step 3: Add Analyzer to Results Dropdown</h3>
<div class="step">
    <p>Go to the <strong>Manage Analyzers</strong> tab above to add your analyzer to the Results dropdown menu.</p>
    <p>After adding the analyzer entry, you must also add its display label to <code>MessageResources.properties</code>.</p>
</div>
</div>

<div class="setup-box">
<h3>Step 4: Create a Lab Sample (Accession)</h3>
<div class="step">
    <p>Before the analyzer can send results, a sample must exist in OpenELIS.</p>
    <p>Register a patient and create a sample order with the tests you mapped in Step 2.</p>
    <p>The <strong>Accession Number</strong> (Lab Number) must match what the analyzer sends.</p>
</div>
</div>

<div class="setup-box">
<h3>Step 5: Configure Analyzer Network Settings</h3>
<div class="step">
    <p>On the physical analyzer (e.g., Mindray BC 5150):</p>
    <table class="ref-table" style="width:auto; margin:10px 0;">
        <tr><th>Setting</th><th>Value</th></tr>
        <tr><td>Connection Mode</td><td>TCP/IP (ASTM)</td></tr>
        <tr><td>Server IP</td><td><code id="serverIp">10.12.13.126</code> (your server IP)</td></tr>
        <tr><td>Port</td><td><code>5100</code></td></tr>
        <tr><td>Protocol</td><td>ASTM E1381-95</td></tr>
    </table>
</div>
</div>

<div class="setup-box">
<h3>Step 6: Start the TCP/IP Bridge</h3>
<div class="step">
    <p>The bridge script listens on TCP port 5100 and forwards results to OpenELIS.</p>
    <p>Start it on the server:</p>
    <pre>docker exec bahmni-standard-openelis-1 python /tmp/analyzer_bridge.py 5100</pre>
    <p>Or run it as a background service:</p>
    <pre>nohup docker exec bahmni-standard-openelis-1 python /tmp/analyzer_bridge.py 5100 &amp;</pre>
</div>
</div>

<div class="setup-box">
<h3>Step 7: Open Firewall Port</h3>
<div class="step">
    <p>Open TCP port 5100 on the server (run as Administrator):</p>
    <pre>netsh advfirewall firewall add rule name="Analyzer TCP 5100" dir=in action=allow protocol=TCP localport=5100</pre>
</div>
</div>

<div class="setup-box">
<h3>Step 8: Test the Connection</h3>
<div class="step">
    <p>Run a test on the analyzer. Results should appear in:</p>
    <p><strong>Results &rarr; Analyzer &rarr; [Your Analyzer Name]</strong></p>
    <p>Review and validate the results to save them to the patient record.</p>
</div>
</div>

<h3>Supported Analyzers (TCP/IP Type Codes)</h3>
<table class="ref-table">
    <tr><th>Analyzer</th><th>Type Code (for URL)</th><th>Action URL</th><th>Status</th></tr>
    <tr><td>Mindray BC 5150</td><td><code>mindraybc</code></td><td><code>/AnalyzerResults.do?type=mindraybc</code></td><td style="color:green">Active</td></tr>
    <tr><td>DxH 800</td><td><code>dxh</code></td><td><code>/AnalyzerResults.do?type=dxh</code></td><td style="color:green">Active</td></tr>
    <tr><td>DxC 700</td><td><code>dxc</code></td><td><code>/AnalyzerResults.do?type=dxc</code></td><td style="color:green">Active</td></tr>
    <tr><td>HumaStar 200</td><td><code>humastar</code></td><td><code>/AnalyzerResults.do?type=humastar</code></td><td style="color:green">Active</td></tr>
    <tr><td>Advia 560</td><td><code>advia</code></td><td><code>/AnalyzerResults.do?type=advia</code></td><td style="color:green">Active</td></tr>
    <tr><td>GeneXpert</td><td><code>genexpert</code></td><td><code>/AnalyzerResults.do?type=genexpert</code></td><td style="color:green">Active</td></tr>
    <tr><td>Sysmex XT 2000</td><td><code>sysmex</code></td><td><code>/AnalyzerResults.do?type=sysmex</code></td><td style="color:green">Active</td></tr>
    <tr><td>Sysmex XN</td><td><code>sysmex_xn</code></td><td><code>/AnalyzerResults.do?type=sysmex_xn</code></td><td style="color:green">Active</td></tr>
    <tr><td>Sysmex KX</td><td><code>sysmex_kx</code></td><td><code>/AnalyzerResults.do?type=sysmex_kx</code></td><td style="color:green">Active</td></tr>
    <tr><td>BC 3000</td><td><code>bc</code></td><td><code>/AnalyzerResults.do?type=bc</code></td><td style="color:green">Active</td></tr>
    <tr><td>Cobas C311</td><td><code>cobas_c311</code></td><td><code>/AnalyzerResults.do?type=cobas_c311</code></td><td style="color:green">Active</td></tr>
    <tr><td>Cobas Integra 400</td><td><code>cobas_integra</code></td><td><code>/AnalyzerResults.do?type=cobas_integra</code></td><td style="color:green">Active</td></tr>
    <tr><td>EXL 200</td><td><code>exl</code></td><td><code>/AnalyzerResults.do?type=exl</code></td><td style="color:green">Active</td></tr>
    <tr><td>ABX Micros ES 60</td><td><code>abx</code></td><td><code>/AnalyzerResults.do?type=abx</code></td><td style="color:green">Active</td></tr>
    <tr><td>DXI 800</td><td><code>dxi_800</code></td><td><code>/AnalyzerResults.do?type=dxi_800</code></td><td style="color:green">Active</td></tr>
    <tr><td>FACSCalibur</td><td><code>facscalibur</code></td><td><code>/AnalyzerResults.do?type=facscalibur</code></td><td style="color:green">Active</td></tr>
    <tr><td>FACSCanto</td><td><code>facscanto</code></td><td><code>/AnalyzerResults.do?type=facscanto</code></td><td style="color:green">Active</td></tr>
    <tr><td>Evolis</td><td><code>evolis</code></td><td><code>/AnalyzerResults.do?type=evolis</code></td><td style="color:green">Active</td></tr>
    <tr><td>Cobas Taqman</td><td><code>cobas_taqman</code></td><td><code>/AnalyzerResults.do?type=cobas_taqman</code></td><td style="color:green">Active</td></tr>
    <tr><td>Cobas DBS</td><td><code>cobasDBS</code></td><td><code>/AnalyzerResults.do?type=cobasDBS</code></td><td style="color:green">Active</td></tr>
</table>
</div>

<!-- TAB 2: Manage Analyzers -->
<div id="tab-manage" class="tab-content">
<%
    String msg = "";
    String msgType = "";

    String dbUrl = "jdbc:postgresql://openelisdb:5432/clinlims";
    String dbUser = "clinlims";
    String dbPass = "clinlims";

    Connection conn = null;
    try {
        Class.forName("org.postgresql.Driver");
        conn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
        conn.setAutoCommit(true);

    } catch (Exception e) { }
%>
<%!
    void updateMessageResource(String key, String value, ServletContext ctx) {
        try {
            String propsPath = ctx.getRealPath("/WEB-INF/classes/MessageResources.properties");
            java.util.Properties props = new java.util.Properties();
            java.io.FileInputStream fis = new java.io.FileInputStream(propsPath);
            props.load(fis);
            fis.close();
            props.setProperty(key, value);
            java.io.FileOutputStream fos = new java.io.FileOutputStream(propsPath);
            props.store(fos, null);
            fos.close();
        } catch (Exception e) { }
    }
%>
<%
    String action = request.getParameter("action");
    if ("add".equals(action) || "update".equals(action)) {
        String elementId = request.getParameter("element_id");
        String displayName = request.getParameter("display_name");
        String displayLabel = request.getParameter("display_label");
        String actionUrl = request.getParameter("action_url");
        String parentId = request.getParameter("parent_id");
        String sortOrder = request.getParameter("presentation_order");
        String newWindow = request.getParameter("new_window");

        if (elementId != null && !elementId.trim().isEmpty() && displayName != null && !displayName.trim().isEmpty()) {
            try {
                if (conn == null || conn.isClosed()) {
                    Class.forName("org.postgresql.Driver");
                    conn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
                    conn.setAutoCommit(true);
                }
                if ("add".equals(action)) {
                    PreparedStatement ps = conn.prepareStatement(
                        "INSERT INTO menu (id, parent_id, presentation_order, element_id, display_key, action_url, new_window) " +
                        "VALUES ((SELECT COALESCE(MAX(id),0)+1 FROM menu), ?, ?, ?, ?, ?, ?)"
                    );
                    ps.setInt(1, Integer.parseInt(parentId != null && !parentId.isEmpty() ? parentId : "300"));
                    ps.setInt(2, Integer.parseInt(sortOrder != null && !sortOrder.isEmpty() ? sortOrder : "10"));
                    ps.setString(3, elementId.trim());
                    ps.setString(4, displayName.trim());
                    ps.setString(5, actionUrl != null ? actionUrl.trim() : "");
                    ps.setBoolean(6, "true".equals(newWindow));
                    ps.executeUpdate();
                    ps.close();
                    if (displayLabel != null && !displayLabel.trim().isEmpty()) {
                        updateMessageResource(displayName.trim(), displayLabel.trim(), application);
                    }
                    msg = "Analyzer '" + elementId + "' added successfully!";
                    msgType = "success";
                } else if ("update".equals(action)) {
                    String id = request.getParameter("id");
                    PreparedStatement ps = conn.prepareStatement(
                        "UPDATE menu SET element_id=?, display_key=?, action_url=?, presentation_order=? WHERE id=?"
                    );
                    ps.setString(1, elementId.trim());
                    ps.setString(2, displayName.trim());
                    ps.setString(3, actionUrl != null ? actionUrl.trim() : "");
                    ps.setInt(4, Integer.parseInt(sortOrder != null && !sortOrder.isEmpty() ? sortOrder : "10"));
                    ps.setInt(5, Integer.parseInt(id));
                    ps.executeUpdate();
                    ps.close();
                    if (displayLabel != null && !displayLabel.trim().isEmpty()) {
                        updateMessageResource(displayName.trim(), displayLabel.trim(), application);
                    }
                    msg = "Analyzer updated successfully!";
                    msgType = "success";
                }
            } catch (Exception e) {
                msg = "Error: " + e.getMessage();
                msgType = "error";
            }
        } else {
            msg = "Element ID and Display Name are required!";
            msgType = "error";
        }
    } else if ("delete".equals(action)) {
        String id = request.getParameter("id");
        if (id != null) {
            try {
                if (conn == null || conn.isClosed()) {
                    Class.forName("org.postgresql.Driver");
                    conn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
                    conn.setAutoCommit(true);
                }
                PreparedStatement ps = conn.prepareStatement("DELETE FROM menu WHERE id=?");
                ps.setInt(1, Integer.parseInt(id));
                ps.executeUpdate();
                ps.close();
                msg = "Analyzer deleted successfully!";
                msgType = "success";
            } catch (Exception e) {
                msg = "Error: " + e.getMessage();
                msgType = "error";
            }
        }
    }
%>

<% if (!msg.isEmpty()) { %>
    <p class="<%= msgType %>"><%= msg %></p>
<% } %>

<h2>Add / Edit Analyzer in Results Dropdown</h2>
<div class="setup-box">
<p><strong>Important:</strong> The <code>type=</code> value in the Action URL <strong>must match</strong> one of the supported type codes listed in the Setup Guide tab. Using an invalid type will cause an Internal Server Error.</p>
</div>
<form method="post" action="AnalyzerConfig.do">
    <input type="hidden" name="action" id="formAction" value="add" />
    <input type="hidden" name="id" id="editId" value="" />
    <table style="width:auto;">
        <tr>
            <td class="label">Element ID <span class="required">*</span>:</td>
            <td><input type="text" name="element_id" id="elementId" placeholder="e.g., mindraybc5150_analyzer_plugin" required /></td>
        </tr>
        <tr>
            <td class="label">Display Name <span class="required">*</span>:</td>
            <td><input type="text" name="display_name" id="displayName" placeholder="e.g., banner.menu.results.mindraybc5150" required /></td>
        </tr>
        <tr>
            <td class="label">Display Label:</td>
            <td><input type="text" name="display_label" id="displayLabel" placeholder="e.g., Hematology: Mindray BC 5150" />
            <br/><small style="color:#888">Friendly name shown in Results dropdown. Saved to MessageResources.properties.</small></td>
        </tr>
        <tr>
            <td class="label">Action URL:</td>
            <td><input type="text" name="action_url" id="actionUrl" placeholder="e.g., /AnalyzerResults.do?type=mindraybc" /></td>
        </tr>
        <tr>
            <td class="label">Parent Menu ID:</td>
            <td><input type="text" name="parent_id" id="parentId" value="300" /> (300 = Analyzer submenu under Results)</td>
        </tr>
        <tr>
            <td class="label">Sort Order:</td>
            <td><input type="text" name="presentation_order" id="sortOrder" value="10" /></td>
        </tr>
        <tr>
            <td class="label">Open in New Window:</td>
            <td><select name="new_window" id="newWindow"><option value="false">No</option><option value="true">Yes</option></select></td>
        </tr>
        <tr>
            <td></td>
            <td>
                <button type="submit" class="btn btn-primary" onclick="document.getElementById('formAction').value='add';">Add Analyzer</button>
                <button type="submit" class="btn btn-primary" onclick="document.getElementById('formAction').value='update';">Update Selected</button>
                <button type="button" class="btn" onclick="resetForm();">Clear</button>
            </td>
        </tr>
    </table>
</form>

<h2>Current Analyzers in Results Dropdown</h2>
<table>
    <tr>
        <th>ID</th>
        <th>Element ID</th>
        <th>Display Label</th>
        <th>Action URL</th>
        <th>Sort</th>
        <th>Actions</th>
    </tr>
<%
    try {
        if (conn == null || conn.isClosed()) {
            Class.forName("org.postgresql.Driver");
            conn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
        }

        Properties props = new Properties();
        String propsPath = getServletContext().getRealPath("/WEB-INF/classes/MessageResources.properties");
        try {
            java.io.FileInputStream fis = new java.io.FileInputStream(propsPath);
            props.load(fis);
            fis.close();
        } catch (Exception e) {}

        Statement st = conn.createStatement();
        ResultSet rs = st.executeQuery(
            "SELECT id, element_id, display_key, action_url, COALESCE(presentation_order,0) as sort_order " +
            "FROM menu WHERE parent_id = 300 ORDER BY presentation_order, id"
        );
        while (rs.next()) {
            int id = rs.getInt("id");
            String elemId = rs.getString("element_id");
            String dispKey = rs.getString("display_key");
            String actUrl = rs.getString("action_url");
            int sortOrder = rs.getInt("sort_order");
            String displayLabel = props.getProperty(dispKey, dispKey);
%>
    <tr>
        <td><%= id %></td>
        <td><%= elemId %></td>
        <td><strong><%= displayLabel %></strong><br/><small style="color:#888"><%= dispKey %></small></td>
        <td><%= actUrl != null ? actUrl : "" %></td>
        <td><%= sortOrder %></td>
        <td>
            <button class="btn" onclick="editRow(<%= id %>, '<%= elemId != null ? elemId.replace("'", "\\'") : "" %>', '<%= dispKey != null ? dispKey.replace("'", "\\'") : "" %>', '<%= actUrl != null ? actUrl.replace("'", "\\'") : "" %>', <%= sortOrder %>, '<%= displayLabel != null ? displayLabel.replace("'", "\\'") : "" %>');">Edit</button>
            <form method="post" action="AnalyzerConfig.do" style="display:inline;" onsubmit="return confirm('Delete this analyzer?');">
                <input type="hidden" name="action" value="delete" />
                <input type="hidden" name="id" value="<%= id %>" />
                <button type="submit" class="btn btn-danger">Delete</button>
            </form>
        </td>
    </tr>
<%
        }
        rs.close();
        st.close();
    } catch (Exception e) {
        out.println("<tr><td colspan='6' class='error'>Error loading data: " + e.getMessage() + "</td></tr>");
    } finally {
        if (conn != null && !conn.isClosed()) conn.close();
    }
%>
</table>
</div>

<!-- TAB 3: Analyzer Database -->
<div id="tab-analyzerdb" class="tab-content">
<%
    String dbMsg2 = "";
    String dbMsgType2 = "";

    Connection conn2 = null;
    try {
        Class.forName("org.postgresql.Driver");
        conn2 = DriverManager.getConnection(dbUrl, dbUser, dbPass);
        conn2.setAutoCommit(true);

        String act2 = request.getParameter("db_action");

        if ("db_add".equals(act2) || "db_update".equals(act2)) {
            String aName = request.getParameter("db_name");
            String aMachineId = request.getParameter("db_machine_id");
            String aDescription = request.getParameter("db_description");
            String aAnalyzerType = request.getParameter("db_analyzer_type");
            String aIsActive = request.getParameter("db_is_active");
            String aLocation = request.getParameter("db_location");
            String aScripId = request.getParameter("db_scrip_id");

            if (aName != null && !aName.trim().isEmpty()) {
                if ("db_add".equals(act2)) {
                    PreparedStatement ps2 = conn2.prepareStatement(
                        "INSERT INTO analyzer (id, name, machine_id, description, analyzer_type, is_active, location, scrip_id, lastupdated) " +
                        "VALUES ((SELECT COALESCE(MAX(id),0)+1 FROM analyzer), ?, ?, ?, ?, ?, ?, ?, NOW())"
                    );
                    ps2.setString(1, aName.trim());
                    ps2.setString(2, aMachineId != null ? aMachineId.trim() : "");
                    ps2.setString(3, aDescription != null ? aDescription.trim() : "");
                    ps2.setString(4, aAnalyzerType != null ? aAnalyzerType.trim() : "");
                    ps2.setBoolean(5, !"false".equals(aIsActive));
                    ps2.setString(6, aLocation != null ? aLocation.trim() : "");
                    if (aScripId != null && !aScripId.trim().isEmpty()) {
                        ps2.setInt(7, Integer.parseInt(aScripId.trim()));
                    } else {
                        ps2.setNull(7, java.sql.Types.NUMERIC);
                    }
                    ps2.executeUpdate();
                    ps2.close();
                    dbMsg2 = "Analyzer '" + aName + "' added successfully!";
                    dbMsgType2 = "success";
                } else if ("db_update".equals(act2)) {
                    String aId = request.getParameter("db_id");
                    PreparedStatement ps2 = conn2.prepareStatement(
                        "UPDATE analyzer SET name=?, machine_id=?, description=?, analyzer_type=?, is_active=?, location=?, scrip_id=?, lastupdated=NOW() WHERE id=?"
                    );
                    ps2.setString(1, aName.trim());
                    ps2.setString(2, aMachineId != null ? aMachineId.trim() : "");
                    ps2.setString(3, aDescription != null ? aDescription.trim() : "");
                    ps2.setString(4, aAnalyzerType != null ? aAnalyzerType.trim() : "");
                    ps2.setBoolean(5, !"false".equals(aIsActive));
                    ps2.setString(6, aLocation != null ? aLocation.trim() : "");
                    if (aScripId != null && !aScripId.trim().isEmpty()) {
                        ps2.setInt(7, Integer.parseInt(aScripId.trim()));
                    } else {
                        ps2.setNull(7, java.sql.Types.NUMERIC);
                    }
                    ps2.setInt(8, Integer.parseInt(aId));
                    ps2.executeUpdate();
                    ps2.close();
                    dbMsg2 = "Analyzer updated successfully!";
                    dbMsgType2 = "success";
                }
            } else {
                dbMsg2 = "Analyzer Name is required!";
                dbMsgType2 = "error";
            }
        } else if ("db_delete".equals(act2)) {
            String aId = request.getParameter("db_id");
            if (aId != null) {
                PreparedStatement psDel = conn2.prepareStatement(
                    "DELETE FROM analyzer_test_map WHERE analyzer_id=?"
                );
                psDel.setInt(1, Integer.parseInt(aId));
                psDel.executeUpdate();
                psDel.close();

                PreparedStatement ps2 = conn2.prepareStatement("DELETE FROM analyzer WHERE id=?");
                ps2.setInt(1, Integer.parseInt(aId));
                ps2.executeUpdate();
                ps2.close();
                dbMsg2 = "Analyzer deleted successfully!";
                dbMsgType2 = "success";
            }
        }
    } catch (Exception e) {
        dbMsg2 = "Error: " + e.getMessage();
        dbMsgType2 = "error";
    }
%>

<% if (!dbMsg2.isEmpty()) { %>
    <p class="<%= dbMsgType2 %>"><%= dbMsg2 %></p>
<% } %>

<h2>Analyzer Database Management</h2>
<div class="setup-box">
<p>Manage all analyzer instruments registered in the system. Each analyzer can be linked to test name mappings and results.</p>
</div>

<div style="display:flex; gap:30px; flex-wrap:wrap;">
<div style="flex:1; min-width:350px;">
<h3>Add / Edit Analyzer</h3>
<form method="post" action="AnalyzerConfig.do#tab-analyzerdb" id="dbForm">
    <input type="hidden" name="db_action" id="dbFormAction" value="db_add" />
    <input type="hidden" name="db_id" id="dbEditId" value="" />
    <table style="width:auto;">
        <tr>
            <td class="label">Name <span class="required">*</span>:</td>
            <td><input type="text" name="db_name" id="dbName" placeholder="e.g., Mindray BC 5150" required style="width:250px;" /></td>
        </tr>
        <tr>
            <td class="label">Machine ID:</td>
            <td><input type="text" name="db_machine_id" id="dbMachineId" placeholder="e.g., 1" style="width:250px;" /></td>
        </tr>
        <tr>
            <td class="label">Description:</td>
            <td><input type="text" name="db_description" id="dbDescription" placeholder="e.g., 5-part hematology" style="width:250px;" /></td>
        </tr>
        <tr>
            <td class="label">Analyzer Type:</td>
            <td><input type="text" name="db_analyzer_type" id="dbAnalyzerType" placeholder="e.g., hematology" style="width:250px;" /></td>
        </tr>
        <tr>
            <td class="label">Script ID:</td>
            <td><input type="text" name="db_scrip_id" id="dbScripId" placeholder="e.g., 1" style="width:250px;" /></td>
        </tr>
        <tr>
            <td class="label">Location:</td>
            <td><input type="text" name="db_location" id="dbLocation" placeholder="e.g., Main Lab" style="width:250px;" /></td>
        </tr>
        <tr>
            <td class="label">Active:</td>
            <td><select name="db_is_active" id="dbIsActive" style="width:250px;"><option value="true">Yes</option><option value="false">No</option></select></td>
        </tr>
        <tr>
            <td></td>
            <td>
                <button type="submit" class="btn btn-primary" onclick="document.getElementById('dbFormAction').value='db_add';">Add Analyzer</button>
                <button type="submit" class="btn btn-primary" onclick="document.getElementById('dbFormAction').value='db_update';">Update</button>
                <button type="button" class="btn" onclick="resetDbForm();">Clear</button>
            </td>
        </tr>
    </table>
</form>
</div>
</div>

<h3>All Analyzers</h3>
<div style="margin:10px 0; display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
    <label><strong>Search:</strong></label>
    <input type="text" id="dbFilterSearch" placeholder="Name, description..." oninput="filterDbTable()" style="width:300px;" />
    <label><strong>Status:</strong></label>
    <select id="dbFilterActive" onchange="filterDbTable()" style="width:120px;">
        <option value="">All</option>
        <option value="true">Active</option>
        <option value="false">Inactive</option>
    </select>
    <button class="btn" onclick="document.getElementById('dbFilterSearch').value='';document.getElementById('dbFilterActive').value='';filterDbTable();">Reset Filters</button>
    <span id="dbCount" style="margin-left:auto; font-weight:bold;"></span>
</div>

<table id="dbTable">
    <thead>
    <tr>
        <th style="cursor:pointer;" onclick="sortDbTable(0)">ID &#x25B4;&#x25BE;</th>
        <th style="cursor:pointer;" onclick="sortDbTable(1)">Name &#x25B4;&#x25BE;</th>
        <th>Description</th>
        <th style="cursor:pointer;" onclick="sortDbTable(3)">Dropdown &#x25B4;&#x25BE;</th>
        <th style="cursor:pointer;" onclick="sortDbTable(4)">Mappings &#x25B4;&#x25BE;</th>
        <th style="cursor:pointer;" onclick="sortDbTable(5)">Active &#x25B4;&#x25BE;</th>
        <th>Last Updated</th>
        <th>Actions</th>
    </tr>
    </thead>
    <tbody>
<%
    try {
        if (conn2 == null || conn2.isClosed()) {
            Class.forName("org.postgresql.Driver");
            conn2 = DriverManager.getConnection(dbUrl, dbUser, dbPass);
        }
        Statement st2 = conn2.createStatement();
        ResultSet rs2 = st2.executeQuery(
            "SELECT a.id, a.name, COALESCE(a.description,'') as description, " +
            "a.is_active, a.lastupdated, " +
            "COALESCE(m.menu_count, 0) as menu_count, " +
            "COALESCE(t.map_count, 0) as map_count " +
            "FROM analyzer a " +
            "LEFT JOIN (SELECT 1 as one, COUNT(*) as menu_count FROM menu WHERE parent_id = 300) m ON 1=1 " +
            "LEFT JOIN (SELECT analyzer_id, COUNT(*) as map_count FROM analyzer_test_map GROUP BY analyzer_id) t ON a.id = t.analyzer_id " +
            "ORDER BY a.id"
        );
        while (rs2.next()) {
            int id2 = rs2.getInt("id");
            String name2 = rs2.getString("name");
            String desc2 = rs2.getString("description");
            boolean isActive2 = rs2.getBoolean("is_active");
            String lastUpd2 = rs2.getTimestamp("lastupdated") != null ? rs2.getTimestamp("lastupdated").toString().substring(0,19) : "";
            int mapCount = rs2.getInt("map_count");
            String activeStr2 = isActive2 ? "true" : "false";
            String activeLabel2 = isActive2 ? "<span style=\"color:green\">Yes</span>" : "<span style=\"color:red\">No</span>";

            boolean hasDropdown = false;
            String nameLower = name2.toLowerCase().replaceAll("[^a-z0-9]", "");
            String nameFirst = name2.toLowerCase().split("\\s+")[0].replaceAll("[^a-z]", "");
            Statement stCheck = conn2.createStatement();
            ResultSet rsCheck = stCheck.executeQuery(
                "SELECT COUNT(*) FROM menu WHERE parent_id = 300 AND " +
                "(LOWER(element_id) LIKE '%" + nameLower + "%' OR LOWER(display_key) LIKE '%" + nameLower + "%' OR " +
                "LOWER(element_id) LIKE '%" + nameFirst + "%' OR LOWER(display_key) LIKE '%" + nameFirst + "%')"
            );
            if (rsCheck.next()) hasDropdown = rsCheck.getInt(1) > 0;
            rsCheck.close();
            stCheck.close();

            String dropLabel = hasDropdown ? "<span style=\"color:green\">&#10003;</span>" : "<span style=\"color:red\">&#10007;</span>";
            String mapLabel = mapCount > 0 ? "<span style=\"color:green\">" + mapCount + " tests</span>" : "<span style=\"color:red\">0 tests</span>";
            String searchStr = (name2 + " " + desc2).toLowerCase();
%>
    <tr data-search="<%= searchStr %>" data-active="<%= activeStr2 %>" data-dropdown="<%= hasDropdown %>">
        <td><%= id2 %></td>
        <td><strong><%= name2 %></strong></td>
        <td><%= desc2 %></td>
        <td><%= dropLabel %></td>
        <td><%= mapLabel %></td>
        <td><%= activeLabel2 %></td>
        <td><%= lastUpd2 %></td>
        <td>
            <button class="btn" onclick="editDbRow(<%= id2 %>, '<%= name2.replace("'", "\\'") %>', '', '<%= desc2.replace("'", "\\'") %>', '', '<%= activeStr2 %>', '', 0);">Edit</button>
            <form method="post" action="AnalyzerConfig.do#tab-analyzerdb" style="display:inline;" onsubmit="return confirm('Delete this analyzer and all its test mappings?');">
                <input type="hidden" name="db_action" value="db_delete" />
                <input type="hidden" name="db_id" value="<%= id2 %>" />
                <button type="submit" class="btn btn-danger">Delete</button>
            </form>
        </td>
    </tr>
<%
        }
        rs2.close();
        st2.close();
    } catch (Exception e) {
        out.println("<tr><td colspan='8' class='error'>Error: " + e.getMessage() + "</td></tr>");
    } finally {
        if (conn2 != null && !conn2.isClosed()) conn2.close();
    }
%>
    </tbody>
</table>
</div>

<!-- TAB 5: Test Name Mapping -->
<div id="tab-testmap" class="tab-content">
<h2>Test Name Mapping Reference</h2>
<div class="setup-box">
<h3>How Test Name Mapping Works</h3>
<p>When the analyzer sends results, it uses its own test names (e.g., <code>WBC</code>, <code>RBC</code>).</p>
<p>OpenELIS needs to know which internal test each analyzer test name corresponds to.</p>
<p>This mapping is stored in the <code>analyzer_test_map</code> database table.</p>
</div>

<h3>Mindray BC 5150 - Standard Test Name Mappings</h3>
<table class="ref-table">
    <tr><th>Analyzer Test Name</th><th>Unit</th><th>OpenELIS Test</th></tr>
    <tr><td>WBC</td><td>10^3/uL</td><td>White Blood Cell Count</td></tr>
    <tr><td>RBC</td><td>10^6/uL</td><td>Red Blood Cell Count</td></tr>
    <tr><td>HGB</td><td>g/dL</td><td>Hemoglobin</td></tr>
    <tr><td>HCT</td><td>%</td><td>Hematocrit</td></tr>
    <tr><td>MCV</td><td>fL</td><td>Mean Corpuscular Volume</td></tr>
    <tr><td>MCH</td><td>pg</td><td>Mean Corpuscular Hemoglobin</td></tr>
    <tr><td>MCHC</td><td>g/dL</td><td>Mean Corpuscular Hemoglobin Concentration</td></tr>
    <tr><td>PLT</td><td>10^3/uL</td><td>Platelet Count</td></tr>
    <tr><td>LYM%</td><td>%</td><td>Lymphocyte Percentage</td></tr>
    <tr><td>LYM#</td><td>10^3/uL</td><td>Lymphocyte Count</td></tr>
    <tr><td>MON%</td><td>%</td><td>Monocyte Percentage</td></tr>
    <tr><td>MON#</td><td>10^3/uL</td><td>Monocyte Count</td></tr>
    <tr><td>NEU%</td><td>%</td><td>Neutrophil Percentage</td></tr>
    <tr><td>NEU#</td><td>10^3/uL</td><td>Neutrophil Count</td></tr>
    <tr><td>EOS%</td><td>%</td><td>Eosinophil Percentage</td></tr>
    <tr><td>EOS#</td><td>10^3/uL</td><td>Eosinophil Count</td></tr>
    <tr><td>BAS%</td><td>%</td><td>Basophil Percentage</td></tr>
    <tr><td>BAS#</td><td>10^3/uL</td><td>Basophil Count</td></tr>
    <tr><td>RDW-CV</td><td>%</td><td>Red Cell Distribution Width CV</td></tr>
    <tr><td>RDW-SD</td><td>fL</td><td>Red Cell Distribution Width SD</td></tr>
    <tr><td>MPV</td><td>fL</td><td>Mean Platelet Volume</td></tr>
    <tr><td>PDW</td><td>%</td><td>Platelet Distribution Width</td></tr>
    <tr><td>P-LCR</td><td>%</td><td>Platelet Large Cell Ratio</td></tr>
</table>

<h3>Manage Mappings</h3>
<p>Go to <strong>Administration &rarr; Analyzer Test Names</strong> in the left menu to add, edit, or delete test name mappings.</p>
<p><strong>Important:</strong> Analyzer test names are <strong>case-sensitive</strong> and must match exactly what the analyzer sends.</p>
</div>

<!-- TAB 5: TCP/IP Bridge -->
<div id="tab-tcp" class="tab-content">
<%
    String tcpMsg = "";
    String tcpMsgType = "";
    Connection connTcp = null;
    try {
        Class.forName("org.postgresql.Driver");
        connTcp = DriverManager.getConnection(dbUrl, dbUser, dbPass);
        connTcp.setAutoCommit(true);

        String tcpAction = request.getParameter("tcp_action");

        if ("save".equals(tcpAction)) {
            String cfgId = request.getParameter("cfg_id");
            String port = request.getParameter("tcp_port");
            String protocol = request.getParameter("tcp_protocol");
            String machineName = request.getParameter("tcp_machine_name");
            String url = request.getParameter("tcp_url");
            if (cfgId != null && port != null) {
                PreparedStatement ps = connTcp.prepareStatement(
                    "UPDATE analyzer_bridge_config SET listen_port=?, protocol=?, machine_name=?, openelis_url=?, updated=NOW() WHERE id=?"
                );
                ps.setInt(1, Integer.parseInt(port));
                ps.setString(2, protocol != null ? protocol : "ASTM");
                ps.setString(3, machineName != null ? machineName : "");
                ps.setString(4, url != null && !url.isEmpty() ? url : "http://localhost:8052/openelis/addAnalyzerData");
                ps.setInt(5, Integer.parseInt(cfgId));
                ps.executeUpdate();
                ps.close();
                tcpMsg = "Bridge config updated!";
                tcpMsgType = "success";
            }
        } else if ("start".equals(tcpAction)) {
            String cfgId = request.getParameter("cfg_id");
            if (cfgId != null) {
                PreparedStatement ps = connTcp.prepareStatement(
                    "UPDATE analyzer_bridge_config SET is_running=true, last_started=NOW(), pid=0, updated=NOW() WHERE id=?"
                );
                ps.setInt(1, Integer.parseInt(cfgId));
                ps.executeUpdate();
                ps.close();
                tcpMsg = "Bridge marked as started!";
                tcpMsgType = "success";
            }
        } else if ("stop".equals(tcpAction)) {
            String cfgId = request.getParameter("cfg_id");
            if (cfgId != null) {
                PreparedStatement ps = connTcp.prepareStatement(
                    "UPDATE analyzer_bridge_config SET is_running=false, last_stopped=NOW(), pid=0, updated=NOW() WHERE id=?"
                );
                ps.setInt(1, Integer.parseInt(cfgId));
                ps.executeUpdate();
                ps.close();
                tcpMsg = "Bridge marked as stopped!";
                tcpMsgType = "success";
            }
        } else if ("start_all".equals(tcpAction)) {
            connTcp.createStatement().executeUpdate(
                "UPDATE analyzer_bridge_config SET is_running=true, last_started=NOW(), updated=NOW()"
            );
            tcpMsg = "All bridges started!";
            tcpMsgType = "success";
        } else if ("stop_all".equals(tcpAction)) {
            connTcp.createStatement().executeUpdate(
                "UPDATE analyzer_bridge_config SET is_running=false, last_stopped=NOW(), updated=NOW()"
            );
            tcpMsg = "All bridges stopped!";
            tcpMsgType = "success";
        }
    } catch (Exception e) {
        tcpMsg = "Error: " + e.getMessage();
        tcpMsgType = "error";
    }
%>
<% if (!tcpMsg.isEmpty()) { %>
    <p class="<%= tcpMsgType %>"><%= tcpMsg %></p>
<% } %>

<h2>TCP/IP Bridge Configuration</h2>
<div class="setup-box">
<h3 style="margin-top:0">How the Bridge Works</h3>
<p>OpenELIS does not have a built-in TCP socket listener. Each analyzer needs a bridge script to:</p>
<ol>
    <li>Listen on a dedicated TCP port for ASTM protocol data from the analyzer</li>
    <li>Parse the ASTM messages to extract accession numbers, test names, and results</li>
    <li>Forward the parsed results to OpenELIS via HTTP POST to <code>/addAnalyzerData</code></li>
</ol>
<p>Bridge script location: <code>/tmp/analyzer_bridge.py</code> inside the OpenELIS container.</p>
</div>

<div style="margin:10px 0; display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
    <form method="post" action="AnalyzerConfig.do#tab-tcp" style="display:inline;">
        <input type="hidden" name="tcp_action" value="start_all" />
        <button type="submit" class="btn btn-success">Start All Bridges</button>
    </form>
    <form method="post" action="AnalyzerConfig.do#tab-tcp" style="display:inline;">
        <input type="hidden" name="tcp_action" value="stop_all" />
        <button type="submit" class="btn btn-danger">Stop All Bridges</button>
    </form>
</div>

<div style="margin:10px 0; display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
    <label><strong>Search:</strong></label>
    <input type="text" id="tcpFilterSearch" placeholder="Analyzer name, machine name, port..." oninput="tcpFilterTable()" style="width:280px;" />
    <label><strong>Status:</strong></label>
    <select id="tcpFilterStatus" onchange="tcpFilterTable()" style="width:120px;">
        <option value="">All</option>
        <option value="true">Running</option>
        <option value="false">Stopped</option>
    </select>
    <label><strong>Protocol:</strong></label>
    <select id="tcpFilterProtocol" onchange="tcpFilterTable()" style="width:120px;">
        <option value="">All</option>
        <option value="ASTM">ASTM</option>
        <option value="CSV">CSV</option>
        <option value="HL7">HL7</option>
    </select>
    <label><strong>Port Range:</strong></label>
    <select id="tcpFilterPort" onchange="tcpFilterTable()" style="width:150px;">
        <option value="">All Ports</option>
        <option value="5100-5105">5100-5105</option>
        <option value="5106-5110">5106-5110</option>
    </select>
    <button class="btn" onclick="document.getElementById('tcpFilterSearch').value='';document.getElementById('tcpFilterStatus').value='';document.getElementById('tcpFilterProtocol').value='';document.getElementById('tcpFilterPort').value='';tcpFilterTable();">Reset</button>
    <span id="tcpStatusCount" style="margin-left:auto; font-weight:bold;"></span>
</div>

<table id="tcpTable">
    <thead>
    <tr>
        <th style="cursor:pointer;" onclick="tcpSortTable(0)">ID &#x25B4;&#x25BE;</th>
        <th style="cursor:pointer;" onclick="tcpSortTable(1)">Analyzer &#x25B4;&#x25BE;</th>
        <th style="cursor:pointer;" onclick="tcpSortTable(2)">Port &#x25B4;&#x25BE;</th>
        <th style="cursor:pointer;" onclick="tcpSortTable(3)">Protocol &#x25B4;&#x25BE;</th>
        <th>Machine Name</th>
        <th>OpenELIS URL</th>
        <th style="cursor:pointer;" onclick="tcpSortTable(6)">Status &#x25B4;&#x25BE;</th>
        <th>Last Started</th>
        <th>Actions</th>
    </tr>
    </thead>
    <tbody>
<%
    try {
        if (connTcp == null || connTcp.isClosed()) {
            Class.forName("org.postgresql.Driver");
            connTcp = DriverManager.getConnection(dbUrl, dbUser, dbPass);
        }
        Statement stTcp = connTcp.createStatement();
        ResultSet rsTcp = stTcp.executeQuery(
            "SELECT c.id, a.name as aname, c.listen_port, c.protocol, COALESCE(c.machine_name,'') as machine_name, " +
            "COALESCE(c.openelis_url,'') as openelis_url, c.is_running, " +
            "c.last_started, c.last_stopped " +
            "FROM analyzer_bridge_config c " +
            "INNER JOIN analyzer a ON c.analyzer_id = a.id " +
            "ORDER BY a.name"
        );
        while (rsTcp.next()) {
            int cfgId = rsTcp.getInt("id");
            String aName = rsTcp.getString("aname");
            int port = rsTcp.getInt("listen_port");
            String protocol = rsTcp.getString("protocol");
            String machineName = rsTcp.getString("machine_name");
            String url = rsTcp.getString("openelis_url");
            boolean running = rsTcp.getBoolean("is_running");
            String lastStarted = rsTcp.getTimestamp("last_started") != null ? rsTcp.getTimestamp("last_started").toString().substring(0,19) : "-";
            String statusClass = running ? "color:green;font-weight:bold" : "color:red";
            String statusText = running ? "RUNNING" : "STOPPED";
            String statusIcon = running ? "&#9679;" : "&#9675;";
%>
    <tr data-search="<%= (aName + " " + machineName + " " + port).toLowerCase() %>"
        data-running="<%= running %>"
        data-protocol="<%= protocol %>"
        data-port="<%= port %>">
        <td><%= cfgId %></td>
        <td><strong><%= aName %></strong></td>
        <td><%= port %></td>
        <td><%= protocol %></td>
        <td><%= machineName %></td>
        <td style="font-size:11px;"><%= url %></td>
        <td style="<%= statusClass %>"><%= statusIcon %> <%= statusText %></td>
        <td style="font-size:11px;"><%= lastStarted %></td>
        <td>
            <button class="btn" onclick="editTcp(<%= cfgId %>, <%= port %>, '<%= protocol %>', '<%= machineName.replace("'", "\\'") %>', '<%= url.replace("'", "\\'") %>');">Edit</button>
<% if (running) { %>
            <form method="post" action="AnalyzerConfig.do#tab-tcp" style="display:inline;">
                <input type="hidden" name="tcp_action" value="stop" />
                <input type="hidden" name="cfg_id" value="<%= cfgId %>" />
                <button type="submit" class="btn btn-danger">Stop</button>
            </form>
<% } else { %>
            <form method="post" action="AnalyzerConfig.do#tab-tcp" style="display:inline;">
                <input type="hidden" name="tcp_action" value="start" />
                <input type="hidden" name="cfg_id" value="<%= cfgId %>" />
                <button type="submit" class="btn btn-success">Start</button>
            </form>
<% } %>
        </td>
    </tr>
<%
        }
        rsTcp.close();
        stTcp.close();
    } catch (Exception e) {
        out.println("<tr><td colspan='9' class='error'>Error: " + e.getMessage() + "</td></tr>");
    } finally {
        if (connTcp != null && !connTcp.isClosed()) connTcp.close();
    }
%>
    </tbody>
</table>

<div class="setup-box" style="margin-top:20px;">
<h3 style="margin-top:0;">Edit Bridge Configuration</h3>
<form method="post" action="AnalyzerConfig.do#tab-tcp" id="tcpForm">
    <input type="hidden" name="tcp_action" value="save" />
    <input type="hidden" name="cfg_id" id="tcpCfgId" value="" />
    <table style="width:auto;">
        <tr>
            <td class="label">Listen Port <span class="required">*</span>:</td>
            <td><input type="number" name="tcp_port" id="tcpPort" min="1024" max="65535" required style="width:150px;" />
            <br/><small style="color:#888">TCP port the bridge listens on (1024-65535)</small></td>
        </tr>
        <tr>
            <td class="label">Protocol:</td>
            <td><select name="tcp_protocol" id="tcpProtocol" style="width:150px;">
                <option value="ASTM">ASTM E1381-95</option>
                <option value="CSV">CSV (Simple)</option>
                <option value="HL7">HL7 v2.x</option>
            </select></td>
        </tr>
        <tr>
            <td class="label">Machine Name:</td>
            <td><input type="text" name="tcp_machine_name" id="tcpMachineName" placeholder="e.g., mindray_bc5150" style="width:300px;" />
            <br/><small style="color:#888">Identifies the analyzer in OpenELIS results</small></td>
        </tr>
        <tr>
            <td class="label">OpenELIS URL:</td>
            <td><input type="text" name="tcp_url" id="tcpUrl" placeholder="http://localhost:8052/openelis/addAnalyzerData" style="width:400px;" />
            <br/><small style="color:#888">HTTP endpoint to POST results to</small></td>
        </tr>
        <tr>
            <td></td>
            <td>
                <button type="submit" class="btn btn-primary">Save Configuration</button>
                <button type="button" class="btn" onclick="resetTcpForm();">Clear</button>
            </td>
        </tr>
    </table>
</form>
</div>

<div class="setup-box">
<h3 style="margin-top:0;">Quick Start Commands</h3>
<p>Start a bridge for a specific port (run inside the container):</p>
<pre>docker exec bahmni-standard-openelis-1 python /tmp/analyzer_bridge.py &lt;PORT&gt;</pre>
<p>Example for Mindray BC 5150 on port 5100:</p>
<pre>docker exec bahmni-standard-openelis-1 python /tmp/analyzer_bridge.py 5100</pre>
<p>Start all bridges as background services:</p>
<pre>docker exec -d bahmni-standard-openelis-1 sh -c "for p in 5100 5101 5102 5103 5104 5105 5106 5107 5108 5109 5110; do python /tmp/analyzer_bridge.py $p &amp; done"</pre>
</div>

<div class="setup-box">
<h3 style="margin-top:0;">Firewall Configuration</h3>
<p>Open all analyzer TCP ports (run as Administrator on the host):</p>
<pre>for /L %i in (5100,1,5110) do netsh advfirewall firewall add rule name="Analyzer TCP %i" dir=in action=allow protocol=TCP localport=%i</pre>
</div>

<div class="setup-box">
<h3 style="margin-top:0;">Test Without a Physical Analyzer</h3>
<p>Send a CSV test result to port 5100:</p>
<pre>echo "TEST-001,WBC,7.5,10^3/uL" | nc localhost 5100</pre>
<p>Send ASTM format:</p>
<pre>printf "H|\\^\\&|||OpenELIS\\rP|1|||SAMPLE001\\rR|1|WBC^7.5^10^3/uL\\r\\x03" | nc localhost 5100</pre>
</div>
</div>

<script>
function showTab(name) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
    document.getElementById('tab-' + name).classList.add('active');
    event.target.classList.add('active');
    if (name === 'analyzerdb') filterDbTable();
}
function editRow(id, elemId, dispKey, actUrl, sortOrder, label) {
    showTab('manage');
    document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab')[1].classList.add('active');
    document.getElementById('formAction').value = 'update';
    document.getElementById('editId').value = id;
    document.getElementById('elementId').value = elemId;
    document.getElementById('displayName').value = dispKey;
    document.getElementById('displayLabel').value = label || '';
    document.getElementById('actionUrl').value = actUrl;
    document.getElementById('sortOrder').value = sortOrder;
    window.scrollTo(0, 0);
}
function resetForm() {
    document.getElementById('formAction').value = 'add';
    document.getElementById('editId').value = '';
    document.getElementById('elementId').value = '';
    document.getElementById('displayName').value = '';
    document.getElementById('displayLabel').value = '';
    document.getElementById('actionUrl').value = '';
    document.getElementById('parentId').value = '300';
    document.getElementById('sortOrder').value = '10';
}
function editDbRow(id, name, machineId, desc, type, isActive, loc, scripId) {
    showTab('analyzerdb');
    document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab')[2].classList.add('active');
    document.getElementById('dbFormAction').value = 'db_update';
    document.getElementById('dbEditId').value = id;
    document.getElementById('dbName').value = name;
    document.getElementById('dbMachineId').value = machineId;
    document.getElementById('dbDescription').value = desc;
    document.getElementById('dbAnalyzerType').value = type;
    document.getElementById('dbIsActive').value = isActive;
    document.getElementById('dbLocation').value = loc;
    document.getElementById('dbScripId').value = scripId === null ? '' : scripId;
    window.scrollTo(0, 0);
}
function resetDbForm() {
    document.getElementById('dbFormAction').value = 'db_add';
    document.getElementById('dbEditId').value = '';
    document.getElementById('dbName').value = '';
    document.getElementById('dbMachineId').value = '';
    document.getElementById('dbDescription').value = '';
    document.getElementById('dbAnalyzerType').value = '';
    document.getElementById('dbIsActive').value = 'true';
    document.getElementById('dbLocation').value = '';
    document.getElementById('dbScripId').value = '';
}
function filterDbTable() {
    var search = document.getElementById('dbFilterSearch').value.toLowerCase();
    var activeFilter = document.getElementById('dbFilterActive').value;
    var rows = document.querySelectorAll('#dbTable tbody tr');
    var count = 0;
    rows.forEach(function(row) {
        var searchData = row.getAttribute('data-search') || '';
        var rowActive = row.getAttribute('data-active') || '';
        var matchSearch = !search || searchData.indexOf(search) !== -1;
        var matchActive = !activeFilter || rowActive === activeFilter;
        if (matchSearch && matchActive) {
            row.style.display = '';
            count++;
        } else {
            row.style.display = 'none';
        }
    });
    document.getElementById('dbCount').textContent = count + ' of ' + rows.length + ' analyzers';
}
var dbSortCol = -1;
var dbSortAsc = true;
function sortDbTable(col) {
    var table = document.getElementById('dbTable');
    var tbody = table.querySelector('tbody');
    var rows = Array.from(tbody.querySelectorAll('tr'));
    if (dbSortCol === col) { dbSortAsc = !dbSortAsc; } else { dbSortCol = col; dbSortAsc = true; }
    rows.sort(function(a, b) {
        var aVal = a.cells[col].textContent.trim();
        var bVal = b.cells[col].textContent.trim();
        var aNum = parseFloat(aVal);
        var bNum = parseFloat(bVal);
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return dbSortAsc ? aNum - bNum : bNum - aNum;
        }
        return dbSortAsc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
    });
    rows.forEach(function(row) { tbody.appendChild(row); });
}
function editTcp(cfgId, port, protocol, machineName, url) {
    document.getElementById('tcpCfgId').value = cfgId;
    document.getElementById('tcpPort').value = port;
    document.getElementById('tcpProtocol').value = protocol;
    document.getElementById('tcpMachineName').value = machineName;
    document.getElementById('tcpUrl').value = url;
    window.scrollTo(0, document.getElementById('tcpForm').offsetTop - 100);
}
function resetTcpForm() {
    document.getElementById('tcpCfgId').value = '';
    document.getElementById('tcpPort').value = '';
    document.getElementById('tcpProtocol').value = 'ASTM';
    document.getElementById('tcpMachineName').value = '';
    document.getElementById('tcpUrl').value = 'http://localhost:8052/openelis/addAnalyzerData';
}
function tcpFilterTable() {
    var search = document.getElementById('tcpFilterSearch').value.toLowerCase();
    var status = document.getElementById('tcpFilterStatus').value;
    var protocol = document.getElementById('tcpFilterProtocol').value;
    var portRange = document.getElementById('tcpFilterPort').value;
    var rows = document.querySelectorAll('#tcpTable tbody tr');
    var count = 0, runningCount = 0;
    rows.forEach(function(row) {
        var searchData = row.getAttribute('data-search') || '';
        var rowRunning = row.getAttribute('data-running');
        var rowProtocol = row.getAttribute('data-protocol') || '';
        var rowPort = parseInt(row.getAttribute('data-port')) || 0;
        var matchSearch = !search || searchData.indexOf(search) !== -1;
        var matchStatus = !status || rowRunning === status;
        var matchProtocol = !protocol || rowProtocol === protocol;
        var matchPort = true;
        if (portRange) {
            var parts = portRange.split('-');
            var low = parseInt(parts[0]), high = parseInt(parts[1]);
            matchPort = rowPort >= low && rowPort <= high;
        }
        if (matchSearch && matchStatus && matchProtocol && matchPort) {
            row.style.display = '';
            count++;
            if (rowRunning === 'true') runningCount++;
        } else {
            row.style.display = 'none';
        }
    });
    document.getElementById('tcpStatusCount').textContent = runningCount + ' running / ' + count + ' shown / ' + rows.length + ' total';
}
var tcpSortCol = -1, tcpSortAsc = true;
function tcpSortTable(col) {
    var tbody = document.querySelector('#tcpTable tbody');
    var rows = Array.from(tbody.querySelectorAll('tr'));
    if (tcpSortCol === col) { tcpSortAsc = !tcpSortAsc; } else { tcpSortCol = col; tcpSortAsc = true; }
    rows.sort(function(a, b) {
        var aVal = a.cells[col].textContent.trim();
        var bVal = b.cells[col].textContent.trim();
        var aNum = parseFloat(aVal), bNum = parseFloat(bVal);
        if (!isNaN(aNum) && !isNaN(bNum)) return tcpSortAsc ? aNum - bNum : bNum - aNum;
        return tcpSortAsc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
    });
    rows.forEach(function(r) { tbody.appendChild(r); });
}
function countTcpStatus() {
    var rows = document.querySelectorAll('#tcpTable tbody tr');
    var running = 0;
    rows.forEach(function(r) { if (r.getAttribute('data-running') === 'true') running++; });
    document.getElementById('tcpStatusCount').textContent = running + ' running / ' + rows.length + ' total';
}
tcpFilterTable();
</script>

</div>
</body>
</html:html>
