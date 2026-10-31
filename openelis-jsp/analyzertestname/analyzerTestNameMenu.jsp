<%@ page language="java" contentType="text/html; charset=utf-8"
    import="java.sql.*, java.util.*"%>
<%@ taglib uri="/tags/struts-bean" prefix="bean" %>
<%@ taglib uri="/tags/struts-html" prefix="html" %>
<%@ taglib uri="/tags/struts-logic" prefix="logic" %>

<style>
    #atnTable { border-collapse: collapse; width: 100%; }
    #atnTable th, #atnTable td { border: 1px solid #ccc; padding: 8px; text-align: left; }
    #atnTable th { background: #486086; color: white; cursor: pointer; }
    .atn-btn { padding: 6px 16px; cursor: pointer; border: 1px solid #999; background: #f0f0f0; margin: 2px; }
    .atn-btn-primary { background: #486086; color: white; border: none; }
    .atn-btn-danger { background: #c0392b; color: white; border: none; }
    .atn-success { color: green; font-weight: bold; }
    .atn-error { color: red; font-weight: bold; }
    .atn-filter-bar { margin: 10px 0; display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
    .atn-filter-bar label { font-weight: bold; }
    .atn-count { background: #486086; color: white; padding: 4px 12px; border-radius: 12px; font-size: 13px; }
    .atn-setup-box { background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 15px; margin: 15px 0; }
    .atn-label { font-weight: bold; width: 200px; }
    #atnTestSelect { font-size: 12px; }
</style>

<div style="margin-bottom:15px;">
    <a href="MasterListsPage.do" style="color:#486086;text-decoration:none;font-weight:bold;font-size:14px;">&#8592; Back to Master Lists</a>
</div>

<%
    String dbUrl = "jdbc:postgresql://openelisdb:5432/clinlims";
    String dbUser = "clinlims";
    String dbPass = "clinlims";
    Connection conn = null;
    String msg = "";
    String msgType = "";

    try {
        Class.forName("org.postgresql.Driver");
        conn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
        conn.setAutoCommit(true);

        String action = request.getParameter("atn_action");

        if ("add".equals(action)) {
            String analyzerId = request.getParameter("atn_analyzer_id");
            String analyzerTestName = request.getParameter("atn_test_name");
            String testId = request.getParameter("atn_openelis_test_id");
            if (analyzerId != null && analyzerTestName != null && testId != null &&
                !analyzerId.isEmpty() && !analyzerTestName.isEmpty() && !testId.isEmpty()) {
                PreparedStatement ps = conn.prepareStatement(
                    "INSERT INTO analyzer_test_map (analyzer_id, analyzer_test_name, test_id) VALUES (?, ?, ?)"
                );
                ps.setInt(1, Integer.parseInt(analyzerId));
                ps.setString(2, analyzerTestName.trim());
                ps.setInt(3, Integer.parseInt(testId));
                ps.executeUpdate();
                ps.close();
                msg = "Mapping added successfully!";
                msgType = "success";
            } else {
                msg = "All fields are required!";
                msgType = "error";
            }
        } else if ("update".equals(action)) {
            String analyzerId = request.getParameter("atn_analyzer_id");
            String analyzerTestName = request.getParameter("atn_test_name");
            String testId = request.getParameter("atn_openelis_test_id");
            String oldAnalyzerId = request.getParameter("atn_old_analyzer_id");
            String oldAnalyzerTestName = request.getParameter("atn_old_test_name");
            if (analyzerId != null && analyzerTestName != null && testId != null &&
                oldAnalyzerId != null && oldAnalyzerTestName != null) {
                PreparedStatement ps = conn.prepareStatement(
                    "UPDATE analyzer_test_map SET analyzer_id=?, analyzer_test_name=?, test_id=? WHERE analyzer_id=? AND analyzer_test_name=?"
                );
                ps.setInt(1, Integer.parseInt(analyzerId));
                ps.setString(2, analyzerTestName.trim());
                ps.setInt(3, Integer.parseInt(testId));
                ps.setInt(4, Integer.parseInt(oldAnalyzerId));
                ps.setString(5, oldAnalyzerTestName);
                ps.executeUpdate();
                ps.close();
                msg = "Mapping updated successfully!";
                msgType = "success";
            }
        } else if ("delete".equals(action)) {
            String analyzerId = request.getParameter("del_aid");
            String analyzerTestName = request.getParameter("del_atname");
            if (analyzerId != null && analyzerTestName != null) {
                PreparedStatement ps = conn.prepareStatement(
                    "DELETE FROM analyzer_test_map WHERE analyzer_id=? AND analyzer_test_name=?"
                );
                ps.setInt(1, Integer.parseInt(analyzerId));
                ps.setString(2, analyzerTestName);
                ps.executeUpdate();
                ps.close();
                msg = "Mapping deleted!";
                msgType = "success";
            }
        } else if ("delete_selected".equals(action)) {
            String[] selected = request.getParameterValues("atn_selected_ids");
            if (selected != null && selected.length > 0) {
                PreparedStatement ps = conn.prepareStatement(
                    "DELETE FROM analyzer_test_map WHERE analyzer_id::text || '-' || analyzer_test_name = ?"
                );
                for (String s : selected) {
                    ps.setString(1, s);
                    ps.addBatch();
                }
                ps.executeBatch();
                ps.close();
                msg = selected.length + " mapping(s) deleted!";
                msgType = "success";
            }
        }
    } catch (Exception e) {
        msg = "Error: " + e.getMessage();
        msgType = "error";
    }
%>

<% if (!msg.isEmpty()) { %>
    <p class="atn-<%= msgType %>"><%= msg %></p>
<% } %>

<div class="atn-setup-box">
<h3 style="margin-top:0">Add / Edit Test Name Mapping</h3>
<form method="post" action="AnalyzerTestNameMenu.do" id="atnForm">
    <input type="hidden" name="atn_action" id="atnFormAction" value="add" />
    <input type="hidden" name="atn_old_analyzer_id" id="atnOldAnalyzerId" value="" />
    <input type="hidden" name="atn_old_test_name" id="atnOldTestName" value="" />
    <table style="width:auto;">
        <tr>
            <td class="atn-label">Analyzer <span style="color:red">*</span>:</td>
            <td>
                <select name="atn_analyzer_id" id="atnAnalyzerId" required style="width:300px;">
                    <option value="">-- Select Analyzer --</option>
<%
    try {
        if (conn == null || conn.isClosed()) {
            Class.forName("org.postgresql.Driver");
            conn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
        }
        Statement stA = conn.createStatement();
        ResultSet rsA = stA.executeQuery("SELECT id, name FROM analyzer WHERE is_active = true ORDER BY name");
        while (rsA.next()) {
%>
                    <option value="<%= rsA.getInt("id") %>"><%= rsA.getString("name") %></option>
<%
        }
        rsA.close();
        stA.close();
    } catch (Exception e) { }
%>
                </select>
            </td>
        </tr>
        <tr>
            <td class="atn-label">Analyzer Test Name <span style="color:red">*</span>:</td>
            <td><input type="text" name="atn_test_name" id="atnTestName" placeholder="e.g., WBC, HGB, GLU" required style="width:300px;" />
            <br/><small style="color:#888">Exact name the analyzer sends (case-sensitive)</small></td>
        </tr>
        <tr>
            <td class="atn-label">OpenELIS Test <span style="color:red">*</span>:</td>
            <td>
                <input type="text" id="atnTestSearch" placeholder="Search test name..." oninput="atnFilterTests()" style="width:300px; margin-bottom:4px;" />
                <select name="atn_openelis_test_id" id="atnTestId" size="8" required style="width:300px;">
<%
    try {
        if (conn == null || conn.isClosed()) {
            Class.forName("org.postgresql.Driver");
            conn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
        }
        Statement stT = conn.createStatement();
        ResultSet rsT = stT.executeQuery("SELECT id, name FROM test WHERE is_active = 'Y' ORDER BY name");
        while (rsT.next()) {
%>
                    <option value="<%= rsT.getInt("id") %>"><%= rsT.getString("name") %></option>
<%
        }
        rsT.close();
        stT.close();
    } catch (Exception e) { }
%>
                </select>
            </td>
        </tr>
        <tr>
            <td></td>
            <td>
                <button type="submit" class="atn-btn atn-btn-primary" onclick="document.getElementById('atnFormAction').value='add';">Add Mapping</button>
                <button type="submit" class="atn-btn atn-btn-primary" onclick="document.getElementById('atnFormAction').value='update';">Update</button>
                <button type="button" class="atn-btn" onclick="atnResetForm();">Clear</button>
            </td>
        </tr>
    </table>
</form>
</div>

<div class="atn-filter-bar">
    <label>Analyzer:</label>
    <select id="atnFilterAnalyzer" onchange="atnFilterTable()" style="width:200px;">
        <option value="">All Analyzers</option>
<%
    try {
        if (conn == null || conn.isClosed()) {
            Class.forName("org.postgresql.Driver");
            conn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
        }
        Statement stFA = conn.createStatement();
        ResultSet rsFA = stFA.executeQuery(
            "SELECT DISTINCT a.name FROM analyzer a INNER JOIN analyzer_test_map atm ON a.id = atm.analyzer_id ORDER BY a.name"
        );
        while (rsFA.next()) {
%>
        <option value="<%= rsFA.getString("name") %>"><%= rsFA.getString("name") %></option>
<%
        }
        rsFA.close();
        stFA.close();
    } catch (Exception e) { }
%>
    </select>
    <label>Search:</label>
    <input type="text" id="atnFilterSearch" placeholder="Test name..." oninput="atnFilterTable()" style="width:250px;" />
    <button class="atn-btn" onclick="document.getElementById('atnFilterAnalyzer').value='';document.getElementById('atnFilterSearch').value='';atnFilterTable();">Reset</button>
    <button class="atn-btn atn-btn-danger" onclick="atnDeleteSelected()">Delete Selected</button>
    <span id="atnRowCount" class="atn-count"></span>
</div>

<form method="post" action="AnalyzerTestNameMenu.do" id="atnBulkForm">
    <input type="hidden" name="atn_action" value="delete_selected" />
    <table id="atnTable">
        <thead>
        <tr>
            <th style="width:40px;"><input type="checkbox" id="atnSelectAll" onclick="atnToggleAll()" /></th>
            <th onclick="atnSortTable(1)" style="cursor:pointer;">Analyzer &#x25B4;&#x25BE;</th>
            <th onclick="atnSortTable(2)" style="cursor:pointer;">Analyzer Test Name &#x25B4;&#x25BE;</th>
            <th onclick="atnSortTable(3)" style="cursor:pointer;">Actual Test Name &#x25B4;&#x25BE;</th>
            <th style="width:120px;">Actions</th>
        </tr>
        </thead>
        <tbody>
<%
    try {
        if (conn == null || conn.isClosed()) {
            Class.forName("org.postgresql.Driver");
            conn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
        }
        Statement st = conn.createStatement();
        ResultSet rs = st.executeQuery(
            "SELECT a.id as aid, a.name as aname, atm.analyzer_test_name, t.name as tname " +
            "FROM analyzer_test_map atm " +
            "INNER JOIN analyzer a ON atm.analyzer_id = a.id " +
            "INNER JOIN test t ON atm.test_id = t.id " +
            "ORDER BY a.name, atm.analyzer_test_name"
        );
        while (rs.next()) {
            int aid = rs.getInt("aid");
            String aname = rs.getString("aname");
            String atname = rs.getString("analyzer_test_name");
            String tname = rs.getString("tname");
%>
        <tr data-analyzer="<%= aname %>" data-search="<%= (aname + " " + atname + " " + tname).toLowerCase() %>">
            <td><input type="checkbox" name="atn_selected_ids" value="<%= aid %>-<%= atname %>" class="atn-check" /></td>
            <td><%= aname %></td>
            <td><strong><%= atname %></strong></td>
            <td><%= tname %></td>
            <td>
                <button type="button" class="atn-btn" onclick="atnEdit(<%= aid %>, '<%= atname.replace("'", "\\'") %>', this);">Edit</button>
                <button type="button" class="atn-btn atn-btn-danger" onclick="atnDelete(<%= aid %>, '<%= atname.replace("'", "\\'") %>');">Delete</button>
            </td>
        </tr>
<%
        }
        rs.close();
        st.close();
    } catch (Exception e) {
        out.println("<tr><td colspan='5' class='atn-error'>Error: " + e.getMessage() + "</td></tr>");
    } finally {
        if (conn != null && !conn.isClosed()) conn.close();
    }
%>
        </tbody>
    </table>
</form>

<script>
function atnFilterTable() {
    var analyzer = document.getElementById('atnFilterAnalyzer').value.toLowerCase();
    var search = document.getElementById('atnFilterSearch').value.toLowerCase();
    var rows = document.querySelectorAll('#atnTable tbody tr');
    var count = 0;
    rows.forEach(function(row) {
        var rowAnalyzer = (row.getAttribute('data-analyzer') || '').toLowerCase();
        var searchData = row.getAttribute('data-search') || '';
        var matchA = !analyzer || rowAnalyzer === analyzer;
        var matchS = !search || searchData.indexOf(search) !== -1;
        if (matchA && matchS) { row.style.display = ''; count++; } else { row.style.display = 'none'; }
    });
    document.getElementById('atnRowCount').textContent = count + ' of ' + rows.length + ' mappings';
}
var atnSortCol = -1, atnSortAsc = true;
function atnSortTable(col) {
    var tbody = document.querySelector('#atnTable tbody');
    var rows = Array.from(tbody.querySelectorAll('tr'));
    if (atnSortCol === col) { atnSortAsc = !atnSortAsc; } else { atnSortCol = col; atnSortAsc = true; }
    rows.sort(function(a, b) {
        var aV = a.cells[col].textContent.trim(), bV = b.cells[col].textContent.trim();
        return atnSortAsc ? aV.localeCompare(bV) : bV.localeCompare(aV);
    });
    rows.forEach(function(r) { tbody.appendChild(r); });
}
function atnToggleAll() {
    var c = document.getElementById('atnSelectAll').checked;
    document.querySelectorAll('.atn-check').forEach(function(cb) { cb.checked = c; });
}
function atnEdit(aid, atname, btn) {
    var row = btn.closest('tr');
    var tname = row.cells[3].textContent.trim();
    document.getElementById('atnFormAction').value = 'update';
    document.getElementById('atnOldAnalyzerId').value = aid;
    document.getElementById('atnOldTestName').value = atname;
    document.getElementById('atnAnalyzerId').value = aid;
    document.getElementById('atnTestName').value = atname;
    var sel = document.getElementById('atnTestId');
    for (var i = 0; i < sel.options.length; i++) {
        if (sel.options[i].text === tname) { sel.options[i].selected = true; break; }
    }
    window.scrollTo(0, 0);
}
function atnDelete(aid, atname) {
    if (!confirm('Delete mapping: ' + atname + '?')) return;
    var f = document.createElement('form');
    f.method = 'POST'; f.action = 'AnalyzerTestNameMenu.do';
    var h1 = document.createElement('input'); h1.type='hidden'; h1.name='atn_action'; h1.value='delete'; f.appendChild(h1);
    var h2 = document.createElement('input'); h2.type='hidden'; h2.name='del_aid'; h2.value=aid; f.appendChild(h2);
    var h3 = document.createElement('input'); h3.type='hidden'; h3.name='del_atname'; h3.value=atname; f.appendChild(h3);
    document.body.appendChild(f); f.submit();
}
function atnDeleteSelected() {
    var c = document.querySelectorAll('.atn-check:checked');
    if (c.length === 0) { alert('No rows selected!'); return; }
    if (!confirm('Delete ' + c.length + ' selected mapping(s)?')) return;
    document.getElementById('atnBulkForm').submit();
}
function atnResetForm() {
    document.getElementById('atnFormAction').value = 'add';
    document.getElementById('atnOldAnalyzerId').value = '';
    document.getElementById('atnOldTestName').value = '';
    document.getElementById('atnAnalyzerId').value = '';
    document.getElementById('atnTestName').value = '';
    document.getElementById('atnTestId').selectedIndex = -1;
    document.getElementById('atnTestSearch').value = '';
    atnFilterTests();
}
function atnFilterTests() {
    var s = document.getElementById('atnTestSearch').value.toLowerCase();
    var sel = document.getElementById('atnTestId');
    for (var i = 0; i < sel.options.length; i++) {
        sel.options[i].style.display = sel.options[i].text.toLowerCase().indexOf(s) !== -1 ? '' : 'none';
    }
}
atnFilterTable();
</script>
