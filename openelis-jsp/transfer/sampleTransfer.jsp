<%@ page language="java" contentType="text/html; charset=utf-8"
    import="java.sql.*, java.util.*, java.text.SimpleDateFormat"%>
<%@ taglib uri="/tags/struts-bean" prefix="bean" %>
<%@ taglib uri="/tags/struts-html" prefix="html" %>
<%@ taglib uri="/tags/struts-logic" prefix="logic" %>

<%
    String dbUrl = "jdbc:postgresql://openelisdb:5432/clinlims";
    String dbUser = "clinlims";
    String dbPass = "clinlims";

    // === AJAX endpoint: search patient and return HTML ===
    String searchAction = request.getParameter("searchAction") != null ? request.getParameter("searchAction") : "";
    if ("searchPatient".equals(searchAction)) {
        response.setContentType("text/html; charset=UTF-8");
        String patientId = request.getParameter("patientId") != null ? request.getParameter("patientId").trim() : "";
        StringBuilder sb = new StringBuilder();

        try {
            Class.forName("org.postgresql.Driver");
            Connection sConn = DriverManager.getConnection(dbUrl, dbUser, dbPass);

            PreparedStatement patientStmt = sConn.prepareStatement(
                "SELECT p.id, p.birth_date, p.gender, " +
                "pe.first_name, pe.last_name " +
                "FROM patient p " +
                "JOIN person pe ON p.person_id = pe.id " +
                "LEFT JOIN patient_identity pi ON p.id = pi.patient_id AND pi.identity_type_id = 2 " +
                "WHERE pi.identity_data = ? OR p.uuid = ? " +
                "LIMIT 1");
            patientStmt.setString(1, patientId);
            patientStmt.setString(2, patientId);
            ResultSet patientRs = patientStmt.executeQuery();

            if (!patientRs.next()) {
                sb.append("<div class=\"xf-msg xf-msg-warn\">No patient found with ID: ").append(patientId).append("</div>");
            } else {
                int patientDbId = patientRs.getInt("id");
                String firstName = patientRs.getString("first_name") != null ? patientRs.getString("first_name") : "";
                String lastName = patientRs.getString("last_name") != null ? patientRs.getString("last_name") : "";
                String gender = patientRs.getString("gender") != null ? patientRs.getString("gender") : "";
                java.sql.Date birthDate = patientRs.getDate("birth_date");

                sb.append("<div class=\"xf-patient-card\">");
                sb.append("<p><strong>Patient:</strong> ").append(firstName).append(" ").append(lastName);
                sb.append(" &nbsp; <strong>ID:</strong> ").append(patientId);
                sb.append(" &nbsp; <strong>Gender:</strong> ").append("M".equals(gender) ? "Male" : "F".equals(gender) ? "Female" : gender);
                if (birthDate != null) {
                    long ageMs = System.currentTimeMillis() - birthDate.getTime();
                    int ageYears = (int)(ageMs / (365.25 * 24 * 60 * 60 * 1000));
                    sb.append(" &nbsp; <strong>Age:</strong> ").append(ageYears).append(" years");
                }
                sb.append("</p></div>");

                PreparedStatement sampleStmt2 = sConn.prepareStatement(
                    "SELECT s.id, s.entered_date, s.collection_date, " +
                    "string_agg(t.name, ', ' ORDER BY t.name) as test_names, " +
                    "COUNT(t.id) as test_count, " +
                    "ll.name as current_location, " +
                    "COALESCE(MAX(a.comment), '') AS analysis_comment " +
                    "FROM sample s " +
                    "JOIN sample_human sh ON s.id = sh.samp_id " +
                    "JOIN sample_item si ON s.id = si.samp_id " +
                    "JOIN analysis a ON si.id = a.sampitem_id " +
                    "JOIN test t ON a.test_id = t.id " +
                    "LEFT JOIN lab_location ll ON s.lab_location_id = ll.id " +
                    "WHERE sh.patient_id = ? AND (s.accession_number IS NULL OR s.accession_number = '') " +
                    "GROUP BY s.id, s.entered_date, s.collection_date, ll.name " +
                    "ORDER BY s.entered_date DESC");
                sampleStmt2.setInt(1, patientDbId);
                ResultSet sampleRs2 = sampleStmt2.executeQuery();

                List<String[]> samples = new ArrayList<String[]>();
                while (sampleRs2.next()) {
                    String dbLocation = sampleRs2.getString("current_location");
                    if (dbLocation == null || dbLocation.isEmpty()) {
                        String comment = sampleRs2.getString("analysis_comment");
                        java.util.regex.Matcher m = java.util.regex.Pattern.compile("\\[LAB_LOCATION:([^\\]]+)\\]").matcher(comment != null ? comment : "");
                        if (m.find()) {
                            dbLocation = m.group(1).trim();
                        } else {
                            dbLocation = "Unassigned";
                        }
                    }
                    samples.add(new String[]{
                        String.valueOf(sampleRs2.getInt("id")),
                        sampleRs2.getString("entered_date"),
                        sampleRs2.getString("test_names"),
                        String.valueOf(sampleRs2.getInt("test_count")),
                        dbLocation
                    });
                }
                sampleRs2.close(); sampleStmt2.close();

                if (samples.isEmpty()) {
                    sb.append("<div class=\"xf-msg xf-msg-info\">No pending orders found for this patient. All orders may have already been collected.</div>");
                } else {
                    sb.append("<div style=\"margin-top:10px;\">");
                    sb.append("<p style=\"font-weight:600;color:#2c3e50;font-size:14px;\">Pending Orders (").append(samples.size()).append(" samples, not yet collected)</p>");
                    sb.append("<table class=\"xf-test-table\">");
                    sb.append("<thead><tr>");
                    sb.append("<th><input type=\"checkbox\" id=\"selectAllSamples\" onchange=\"toggleAllSamples(this)\" title=\"Select All\"></th>");
                    sb.append("<th>Sample #</th>");
                    sb.append("<th>Entered Date</th>");
                    sb.append("<th>Tests</th>");
                    sb.append("<th>Count</th>");
                    sb.append("<th>Current Location</th>");
                    sb.append("</tr></thead><tbody>");

                    int row = 0;
                    for (String[] s : samples) {
                        String bg = (row % 2 == 0) ? "" : "background:#f8f9fa;";
                        String entered = s[1] != null && s[1].length() > 16 ? s[1].substring(0, 16).replace("T"," ") : (s[1] != null ? s[1] : "");
                        sb.append("<tr style=\"").append(bg).append("\">");
                        sb.append("<td><input type=\"checkbox\" name=\"sampleIds\" value=\"").append(s[0]).append("\" class=\"sample-checkbox\"></td>");
                        sb.append("<td><strong>#").append(s[0]).append("</strong></td>");
                        sb.append("<td>").append(entered).append("</td>");
                        sb.append("<td style=\"max-width:300px;word-wrap:break-word;font-size:11px;\">").append(s[2] != null ? s[2] : "").append("</td>");
                        sb.append("<td>").append(s[3]).append("</td>");
                        sb.append("<td><span class=\"xf-badge xf-badge-pending\">").append(s[4]).append("</span></td>");
                        sb.append("</tr>");
                        row++;
                    }
                    sb.append("</tbody></table>");
                    sb.append("<p style=\"margin-top:8px;font-size:12px;color:#666;\">Select samples to transfer, then choose destination and reason below.</p>");
                    sb.append("</div>");
                }
                patientRs.close(); patientStmt.close();
            }
            sConn.close();
        } catch (Exception e) {
            sb.append("<div class=\"xf-msg xf-msg-error\">Error: ").append(e.getMessage()).append("</div>");
        }

        out.clear();
        out.print(sb.toString());
        out.flush();
        return;
    }
%>

<style>
    .xf-container { max-width: 900px; margin: 20px auto; font-family: Arial, sans-serif; }
    .xf-section { background: white; border: 1px solid #dee2e6; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
    .xf-section h3 { margin-top: 0; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 8px; font-size: 16px; }
    .xf-tabs { display: flex; gap: 0; margin-bottom: 20px; border-bottom: 2px solid #dee2e6; }
    .xf-tab { padding: 10px 24px; cursor: pointer; border: none; background: #f8f9fa; color: #666; font-size: 14px; font-weight: 600; border-bottom: 3px solid transparent; transition: all 0.2s; }
    .xf-tab:hover { background: #e9ecef; color: #333; }
    .xf-tab.active { background: white; color: #2c3e50; border-bottom-color: #3498db; }
    .xf-tab-panel { display: none; }
    .xf-tab-panel.active { display: block; }
    .xf-form-row { display: flex; gap: 10px; margin-bottom: 12px; align-items: center; }
    .xf-form-row label { font-weight: 600; width: 160px; font-size: 13px; color: #555; }
    .xf-form-row input, .xf-form-row select, .xf-form-row textarea { flex: 1; padding: 8px 12px; font-size: 13px; border: 1px solid #ccc; border-radius: 4px; }
    .xf-form-row textarea { height: 60px; resize: vertical; }
    .xf-form-row input:focus, .xf-form-row select:focus, .xf-form-row textarea:focus { border-color: #3498db; outline: none; box-shadow: 0 0 0 2px rgba(52,152,219,0.15); }
    .xf-btn { padding: 8px 20px; cursor: pointer; border: 1px solid #999; background: #f0f0f0; margin: 2px; font-size: 13px; border-radius: 4px; font-weight: 600; }
    .xf-btn-primary { background: #3498db; color: white; border: none; }
    .xf-btn-primary:hover { background: #2980b9; }
    .xf-btn-success { background: #27ae60; color: white; border: none; }
    .xf-btn-success:hover { background: #219a52; }
    .xf-msg { padding: 10px 14px; border-radius: 6px; margin-bottom: 12px; font-weight: 600; font-size: 13px; }
    .xf-msg-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .xf-msg-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    .xf-msg-info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
    .xf-msg-warn { background: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
    .xf-patient-card { background: #f0f7ff; border: 1px solid #b8daff; border-radius: 6px; padding: 15px; margin: 12px 0; }
    .xf-patient-card p { margin: 3px 0; font-size: 13px; }
    .xf-patient-card strong { color: #2c3e50; }
    .xf-test-table { border-collapse: collapse; width: 100%; margin-top: 10px; font-size: 13px; }
    .xf-test-table th, .xf-test-table td { border: 1px solid #dee2e6; padding: 8px 10px; text-align: left; }
    .xf-test-table th { background: #34495e; color: white; font-weight: 600; }
    .xf-test-table tr:nth-child(even) { background: #f8f9fa; }
    .xf-test-table tr:hover { background: #e9ecef; }
    .xf-test-table input[type="checkbox"] { width: 16px; height: 16px; cursor: pointer; }
    .xf-badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }
    .xf-badge-pending { background: #fff3cd; color: #856404; }
    .xf-badge-collected { background: #d4edda; color: #155724; }
    .xf-badge-transfer { background: #d1ecf1; color: #0c5460; }
    .xf-empty { color: #999; text-align: center; padding: 20px; font-style: italic; }
    .xf-history-table { border-collapse: collapse; width: 100%; margin-top: 10px; font-size: 12px; }
    .xf-history-table th, .xf-history-table td { border: 1px solid #dee2e6; padding: 6px 8px; text-align: left; }
    .xf-history-table th { background: #34495e; color: white; }
    .xf-history-table tr:nth-child(even) { background: #f8f9fa; }
    .xf-select-all { margin: 8px 0; font-size: 13px; color: #555; }
    .xf-select-all label { width: auto; font-weight: normal; cursor: pointer; }
    .xf-hidden { display: none; }
    .xf-loading { color: #999; font-style: italic; padding: 10px; }
</style>

<div style="margin-bottom:15px;">
    <a href="MasterListsPage.do" style="color:#3498db;text-decoration:none;font-weight:bold;font-size:14px;">&#8592; Back to Master Lists</a>
</div>

<%
    String msgType = "";
    String msgText = "";

    int currentUserId = 0;
    try {
        us.mn.state.health.lims.login.valueholder.UserSessionData usd =
            (us.mn.state.health.lims.login.valueholder.UserSessionData) session.getAttribute("userSessionData");
        if (usd != null) currentUserId = usd.getSystemUserId();
    } catch (Exception e) {}

    String currentLocationId = (String) session.getAttribute("selectedLabLocationId");
    String currentLocationName = (String) session.getAttribute("selectedLabLocationName");

    // === Handle transfer action (by accession number) ===
    String transferAction = request.getParameter("transferAction") != null ? request.getParameter("transferAction") : "";
    if ("transfer".equals(transferAction)) {
        String sampleAccession = request.getParameter("sampleAccession") != null ? request.getParameter("sampleAccession").trim() : "";
        String toLocationId = request.getParameter("toLocationId") != null ? request.getParameter("toLocationId") : "";
        String toLocationName = request.getParameter("toLocationName") != null ? request.getParameter("toLocationName") : "";
        String reason = request.getParameter("reason") != null ? request.getParameter("reason").trim() : "";

        if (sampleAccession.isEmpty() || toLocationId.isEmpty() || reason.isEmpty()) {
            msgType = "error";
            msgText = "All fields are required for transfer.";
        } else {
            Connection transConn = null;
            try {
                Class.forName("org.postgresql.Driver");
                transConn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
                transConn.setAutoCommit(false);

                if (toLocationName.isEmpty()) {
                    PreparedStatement locStmt = transConn.prepareStatement("SELECT name FROM lab_location WHERE id = ?");
                    locStmt.setInt(1, Integer.parseInt(toLocationId));
                    ResultSet locRs = locStmt.executeQuery();
                    if (locRs.next()) toLocationName = locRs.getString("name");
                    locRs.close(); locStmt.close();
                }

                PreparedStatement findSample = transConn.prepareStatement(
                    "SELECT s.id, s.lab_location_id, " +
                    "COALESCE(MAX(a.comment), '') AS analysis_comment " +
                    "FROM sample s " +
                    "JOIN sample_item si ON s.id = si.samp_id " +
                    "JOIN analysis a ON si.id = a.sampitem_id " +
                    "WHERE s.accession_number = ? " +
                    "GROUP BY s.id, s.lab_location_id");
                findSample.setString(1, sampleAccession);
                ResultSet sampleRs = findSample.executeQuery();

                if (!sampleRs.next()) {
                    msgType = "error";
                    msgText = "Sample not found with accession number: " + sampleAccession;
                } else {
                    long sampleId = sampleRs.getLong("id");
                    int fromLocId = sampleRs.getInt("lab_location_id");
                    String currentComment = sampleRs.getString("analysis_comment");

                    String fromLocName = "Unassigned";
                    if (fromLocId > 0) {
                        PreparedStatement fromLocStmt = transConn.prepareStatement("SELECT name FROM lab_location WHERE id = ?");
                        fromLocStmt.setInt(1, fromLocId);
                        ResultSet fromLocRs = fromLocStmt.executeQuery();
                        if (fromLocRs.next()) fromLocName = fromLocRs.getString("name");
                        fromLocRs.close(); fromLocStmt.close();
                    } else {
                        java.util.regex.Matcher m = java.util.regex.Pattern.compile("\\[LAB_LOCATION:([^\\]]+)\\]").matcher(currentComment != null ? currentComment : "");
                        if (m.find()) {
                            fromLocName = m.group(1).trim();
                            PreparedStatement resolveStmt = transConn.prepareStatement("SELECT id FROM lab_location WHERE name = ?");
                            resolveStmt.setString(1, fromLocName);
                            ResultSet resolveRs = resolveStmt.executeQuery();
                            if (resolveRs.next()) {
                                fromLocId = resolveRs.getInt("id");
                            }
                            resolveRs.close(); resolveStmt.close();
                            if (fromLocId <= 0) {
                                PreparedStatement createLoc = transConn.prepareStatement(
                                    "INSERT INTO lab_location (name, is_active) VALUES (?, true) RETURNING id");
                                createLoc.setString(1, fromLocName);
                                ResultSet createRs = createLoc.executeQuery();
                                if (createRs.next()) fromLocId = createRs.getInt("id");
                                createRs.close(); createLoc.close();
                            }
                        }
                    }

                    if (fromLocId > 0 && String.valueOf(fromLocId).equals(toLocationId)) {
                        msgType = "error";
                        msgText = "Sample is already at this location.";
                    } else {

                        String newComment = (currentComment != null ? currentComment : "").replaceAll("\\[LAB_LOCATION:[^\\]]*\\]", "[LAB_LOCATION:" + toLocationName + "]");
                        if (!newComment.contains("[LAB_LOCATION:")) {
                            newComment = "[LAB_LOCATION:" + toLocationName + "] " + newComment;
                        }

                        PreparedStatement ins = transConn.prepareStatement(
                            "INSERT INTO sample_transfer (sample_id, from_location_id, to_location_id, transferred_by, reason, status) " +
                            "VALUES (?, ?, ?, ?, ?, 'COMPLETED')");
                        ins.setLong(1, sampleId);
                        ins.setInt(2, fromLocId);
                        ins.setInt(3, Integer.parseInt(toLocationId));
                        ins.setInt(4, currentUserId);
                        ins.setString(5, reason);
                        ins.executeUpdate();
                        ins.close();

                        PreparedStatement updAnalysis = transConn.prepareStatement(
                            "UPDATE analysis SET comment = ? WHERE sampitem_id IN (SELECT id FROM sample_item WHERE samp_id = ?)");
                        updAnalysis.setString(1, newComment);
                        updAnalysis.setLong(2, sampleId);
                        updAnalysis.executeUpdate();
                        updAnalysis.close();

                        PreparedStatement upd = transConn.prepareStatement(
                            "UPDATE sample SET lab_location_id = ? WHERE id = ?");
                        upd.setInt(1, Integer.parseInt(toLocationId));
                        upd.setLong(2, sampleId);
                        upd.executeUpdate();
                        upd.close();

                        PreparedStatement audit = transConn.prepareStatement(
                            "INSERT INTO audit_log (table_name, record_id, action, old_values, new_values, performed_by) " +
                            "VALUES ('sample', ?, 'TRANSFER', ?, ?, ?)");
                        audit.setLong(1, sampleId);
                        audit.setString(2, "{\"lab_location_id\": " + fromLocId + ", \"location_name\": \"" + fromLocName + "\"}");
                        audit.setString(3, "{\"lab_location_id\": " + toLocationId + ", \"location_name\": \"" + toLocationName + "\"}");
                        audit.setInt(4, currentUserId);
                        audit.executeUpdate();
                        audit.close();

                        transConn.commit();
                        msgType = "success";
                        msgText = "Sample " + sampleAccession + " transferred from " + fromLocName + " to " + toLocationName + " successfully.";
                    }
                }
                sampleRs.close(); findSample.close();
            } catch (Exception e) {
                msgType = "error";
                msgText = "Transfer error: " + e.getMessage();
                if (transConn != null) try { transConn.rollback(); } catch (Exception ex) {}
            } finally {
                if (transConn != null) try { transConn.close(); } catch (Exception ex) {}
            }
        }
        transferAction = "";
    }

    // === Handle order transfer action (pre-collection, by patient ID) ===
    String orderTransferAction = request.getParameter("orderTransferAction") != null ? request.getParameter("orderTransferAction") : "";
    if ("orderTransfer".equals(orderTransferAction)) {
        String patientId = request.getParameter("patientIdOrder") != null ? request.getParameter("patientIdOrder").trim() : "";
        String toLocationId = request.getParameter("orderToLocationId") != null ? request.getParameter("orderToLocationId") : "";
        String toLocationName = request.getParameter("orderToLocationName") != null ? request.getParameter("orderToLocationName") : "";
        String reason = request.getParameter("orderReason") != null ? request.getParameter("orderReason").trim() : "";
        String[] sampleIds = request.getParameterValues("sampleIds");

        if (patientId.isEmpty() || toLocationId.isEmpty() || reason.isEmpty()) {
            msgType = "error";
            msgText = "All fields are required for order transfer.";
        } else if (sampleIds == null || sampleIds.length == 0) {
            msgType = "error";
            msgText = "Please select at least one sample/order to transfer.";
        } else {
            Connection transConn = null;
            try {
                Class.forName("org.postgresql.Driver");
                transConn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
                transConn.setAutoCommit(false);

                if (toLocationName.isEmpty()) {
                    PreparedStatement locStmt = transConn.prepareStatement("SELECT name FROM lab_location WHERE id = ?");
                    locStmt.setInt(1, Integer.parseInt(toLocationId));
                    ResultSet locRs = locStmt.executeQuery();
                    if (locRs.next()) toLocationName = locRs.getString("name");
                    locRs.close(); locStmt.close();
                }

                int transferCount = 0;
                for (String sid : sampleIds) {
                    long sampleId = Long.parseLong(sid);

                    PreparedStatement findStmt = transConn.prepareStatement(
                        "SELECT s.lab_location_id, COALESCE(MAX(a.comment), '') AS analysis_comment " +
                        "FROM sample s " +
                        "JOIN sample_item si ON s.id = si.samp_id " +
                        "JOIN analysis a ON si.id = a.sampitem_id " +
                        "WHERE s.id = ? " +
                        "GROUP BY s.lab_location_id");
                    findStmt.setLong(1, sampleId);
                    ResultSet findRs = findStmt.executeQuery();
                    if (!findRs.next()) continue;
                    int fromLocId = findRs.getInt("lab_location_id");
                    String currentComment = findRs.getString("analysis_comment");
                    findRs.close(); findStmt.close();

                    String fromLocName = "Unassigned";
                    if (fromLocId > 0) {
                        PreparedStatement fnStmt = transConn.prepareStatement("SELECT name FROM lab_location WHERE id = ?");
                        fnStmt.setInt(1, fromLocId);
                        ResultSet fnRs = fnStmt.executeQuery();
                        if (fnRs.next()) fromLocName = fnRs.getString("name");
                        fnRs.close(); fnStmt.close();
                    } else {
                        java.util.regex.Matcher m = java.util.regex.Pattern.compile("\\[LAB_LOCATION:([^\\]]+)\\]").matcher(currentComment != null ? currentComment : "");
                        if (m.find()) {
                            fromLocName = m.group(1).trim();
                            PreparedStatement resolveStmt = transConn.prepareStatement("SELECT id FROM lab_location WHERE name = ?");
                            resolveStmt.setString(1, fromLocName);
                            ResultSet resolveRs = resolveStmt.executeQuery();
                            if (resolveRs.next()) fromLocId = resolveRs.getInt("id");
                            resolveRs.close(); resolveStmt.close();
                            if (fromLocId <= 0) {
                                PreparedStatement createLoc = transConn.prepareStatement(
                                    "INSERT INTO lab_location (name, is_active) VALUES (?, true) RETURNING id");
                                createLoc.setString(1, fromLocName);
                                ResultSet createRs = createLoc.executeQuery();
                                if (createRs.next()) fromLocId = createRs.getInt("id");
                                createRs.close(); createLoc.close();
                            }
                        }
                    }

                    String newComment = (currentComment != null ? currentComment : "").replaceAll("\\[LAB_LOCATION:[^\\]]*\\]", "[LAB_LOCATION:" + toLocationName + "]");
                    if (!newComment.contains("[LAB_LOCATION:")) {
                        newComment = "[LAB_LOCATION:" + toLocationName + "] " + newComment;
                    }

                    PreparedStatement ins = transConn.prepareStatement(
                        "INSERT INTO sample_transfer (sample_id, from_location_id, to_location_id, transferred_by, reason, status) " +
                        "VALUES (?, ?, ?, ?, ?, 'COMPLETED')");
                    ins.setLong(1, sampleId);
                    ins.setInt(2, fromLocId > 0 ? fromLocId : 1);
                    ins.setInt(3, Integer.parseInt(toLocationId));
                    ins.setInt(4, currentUserId);
                    ins.setString(5, reason);
                    ins.executeUpdate();
                    ins.close();

                    PreparedStatement audit = transConn.prepareStatement(
                        "INSERT INTO audit_log (table_name, record_id, action, old_values, new_values, performed_by) " +
                        "VALUES ('sample', ?, 'ORDER_TRANSFER', ?, ?, ?)");
                    audit.setLong(1, sampleId);
                    audit.setString(2, "{\"lab_location_id\": " + fromLocId + ", \"location_name\": \"" + fromLocName + "\"}");
                    audit.setString(3, "{\"lab_location_id\": " + toLocationId + ", \"location_name\": \"" + toLocationName + "\"}");
                    audit.setInt(4, currentUserId);
                    audit.executeUpdate();
                    audit.close();

                    PreparedStatement updAnalysis = transConn.prepareStatement(
                        "UPDATE analysis SET comment = ? WHERE sampitem_id IN (SELECT id FROM sample_item WHERE samp_id = ?)");
                    updAnalysis.setString(1, newComment);
                    updAnalysis.setLong(2, sampleId);
                    updAnalysis.executeUpdate();
                    updAnalysis.close();

                    PreparedStatement upd = transConn.prepareStatement(
                        "UPDATE sample SET lab_location_id = ? WHERE id = ?");
                    upd.setInt(1, Integer.parseInt(toLocationId));
                    upd.setLong(2, sampleId);
                    upd.executeUpdate();
                    upd.close();

                    transferCount++;
                }

                transConn.commit();
                msgType = "success";
                msgText = transferCount + " sample(s) for patient " + patientId + " transferred to " + toLocationName + " successfully.";
            } catch (Exception e) {
                msgType = "error";
                msgText = "Order transfer error: " + e.getMessage();
                if (transConn != null) try { transConn.rollback(); } catch (Exception ex) {}
            } finally {
                if (transConn != null) try { transConn.close(); } catch (Exception ex) {}
            }
        }
        orderTransferAction = "";
    }

    // Fetch locations for dropdown
    List<String[]> locations = new ArrayList<String[]>();
    List<String[]> recentTransfers = new ArrayList<String[]>();

    try {
        Class.forName("org.postgresql.Driver");
        Connection conn = DriverManager.getConnection(dbUrl, dbUser, dbPass);

        PreparedStatement locStmt = conn.prepareStatement("SELECT id, name FROM lab_location WHERE is_active = true ORDER BY name");
        ResultSet locRs = locStmt.executeQuery();
        while (locRs.next()) {
            locations.add(new String[]{locRs.getString("id"), locRs.getString("name")});
        }
        locRs.close(); locStmt.close();

        PreparedStatement histStmt = conn.prepareStatement(
            "SELECT st.id, s.accession_number, fl.name as from_name, tl.name as to_name, " +
            "su.login_name as transferred_by_name, st.transfer_date, st.reason, st.status " +
            "FROM sample_transfer st " +
            "JOIN sample s ON st.sample_id = s.id " +
            "JOIN lab_location fl ON st.from_location_id = fl.id " +
            "JOIN lab_location tl ON st.to_location_id = tl.id " +
            "LEFT JOIN system_user su ON st.transferred_by = su.id " +
            "ORDER BY st.transfer_date DESC LIMIT 20");
        ResultSet histRs = histStmt.executeQuery();
        while (histRs.next()) {
            recentTransfers.add(new String[]{
                histRs.getString("accession_number"),
                histRs.getString("from_name"),
                histRs.getString("to_name"),
                histRs.getString("transferred_by_name"),
                histRs.getString("transfer_date"),
                histRs.getString("reason"),
                histRs.getString("status")
            });
        }
        histRs.close(); histStmt.close();
        conn.close();
    } catch (Exception e) {
        msgText = "Error: " + e.getMessage();
    }
%>

<div class="xf-container">
    <% if (!msgText.isEmpty()) { %>
    <div class="xf-msg xf-msg-<%= msgType %>"><%= msgText %></div>
    <% } %>

    <h2 style="text-align:center; color:#2c3e50; margin-bottom:5px;">Sample &amp; Order Transfer</h2>

    <% if (currentLocationId != null) { %>
    <div class="xf-msg xf-msg-info">Current Location: <strong><%= currentLocationName %></strong></div>
    <% } else { %>
    <div class="xf-msg xf-msg-warn">No location selected. Please <a href="LocationSelect.do" style="font-weight:bold;">select a location</a> first.</div>
    <% } %>

    <!-- Tabs -->
    <div class="xf-tabs">
        <div class="xf-tab active" onclick="switchTab('accession')">Transfer by Accession #</div>
        <div class="xf-tab" onclick="switchTab('patient')">Transfer by Patient ID</div>
    </div>

    <!-- Tab 1: Transfer by Accession Number -->
    <div id="tab-accession" class="xf-tab-panel active">
        <div class="xf-section">
            <h3>Transfer Collected Sample</h3>
            <form method="post" action="SampleTransfer.do">
                <input type="hidden" name="transferAction" value="transfer">
                <div class="xf-form-row">
                    <label>Sample Accession #:</label>
                    <input type="text" name="sampleAccession" required placeholder="Enter accession number">
                </div>
                <div class="xf-form-row">
                    <label>Transfer To:</label>
                    <select name="toLocationId" id="toLocation1" required>
                        <option value="">-- Select Destination --</option>
                        <% for (String[] loc : locations) { if (!loc[0].equals(currentLocationId)) { %>
                        <option value="<%= loc[0] %>" data-name="<%= loc[1] %>"><%= loc[1] %></option>
                        <% } } %>
                    </select>
                    <input type="hidden" name="toLocationName" id="toLocationName1">
                </div>
                <div class="xf-form-row">
                    <label>Reason for Transfer *:</label>
                    <textarea name="reason" required placeholder="Enter reason for transfer"></textarea>
                </div>
                <div style="text-align:right;">
                    <button type="submit" class="xf-btn xf-btn-primary" onclick="return confirm('Confirm sample transfer?')">Transfer Sample</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Tab 2: Transfer by Patient ID -->
    <div id="tab-patient" class="xf-tab-panel">
        <div class="xf-section">
            <h3>Transfer Pending Orders (Before Collection)</h3>
            <form method="post" action="SampleTransfer.do" id="orderTransferForm">
                <input type="hidden" name="orderTransferAction" value="orderTransfer">
                <input type="hidden" name="patientIdOrder" id="patientIdOrderHidden">

                <div class="xf-form-row">
                    <label>Patient ID:</label>
                    <input type="text" id="patientIdInput" placeholder="Enter patient ID (e.g. 124264)" onkeypress="if(event.key==='Enter'){searchPatient(); return false;}">
                    <button type="button" class="xf-btn xf-btn-primary" onclick="searchPatient()">Search</button>
                </div>

                <div id="patientResults" class="xf-hidden"></div>

                <div id="orderTransferSection" class="xf-hidden" style="margin-top:15px;">
                    <div class="xf-form-row">
                        <label>Transfer To:</label>
                        <select name="orderToLocationId" id="toLocation2" required>
                            <option value="">-- Select Destination --</option>
                            <% for (String[] loc : locations) { if (!loc[0].equals(currentLocationId)) { %>
                            <option value="<%= loc[0] %>" data-name="<%= loc[1] %>"><%= loc[1] %></option>
                            <% } } %>
                        </select>
                        <input type="hidden" name="orderToLocationName" id="toLocationName2">
                    </div>
                    <div class="xf-form-row">
                        <label>Reason for Transfer *:</label>
                        <textarea name="orderReason" id="orderReason" required placeholder="Enter reason for transfer"></textarea>
                    </div>
                    <div style="text-align:right;">
                        <button type="submit" class="xf-btn xf-btn-success" onclick="return confirmOrderTransfer()">Transfer Selected Orders</button>
                    </div>
                </div>
            </form>
        </div>
    </div>

    <!-- Transfer History -->
    <div class="xf-section">
        <h3>Recent Transfers</h3>
        <% if (recentTransfers.isEmpty()) { %>
        <p class="xf-empty">No transfers recorded yet.</p>
        <% } else { %>
        <table class="xf-history-table">
            <thead>
                <tr>
                    <th>Accession #</th>
                    <th>From</th>
                    <th>To</th>
                    <th>By</th>
                    <th>Date</th>
                    <th>Reason</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <% for (String[] t : recentTransfers) { %>
                <tr>
                    <td><strong><%= t[0] != null ? t[0] : "Pre-collection" %></strong></td>
                    <td><%= t[1] %></td>
                    <td><%= t[2] %></td>
                    <td><%= t[3] %></td>
                    <td><%= t[4] != null ? t[4].substring(0, Math.min(19, t[4].length())).replace("T"," ") : "" %></td>
                    <td><%= t[5] %></td>
                    <td><strong style="color:<%= "COMPLETED".equals(t[6]) ? "#27ae60" : "#e67e22" %>"><%= t[6] %></strong></td>
                </tr>
                <% } %>
            </tbody>
        </table>
        <% } %>
    </div>
</div>

<script>
function switchTab(tab) {
    document.querySelectorAll('.xf-tab').forEach(function(t) { t.classList.remove('active'); });
    document.querySelectorAll('.xf-tab-panel').forEach(function(p) { p.classList.remove('active'); });
    if (tab === 'accession') {
        document.querySelectorAll('.xf-tab')[0].classList.add('active');
        document.getElementById('tab-accession').classList.add('active');
    } else {
        document.querySelectorAll('.xf-tab')[1].classList.add('active');
        document.getElementById('tab-patient').classList.add('active');
    }
}

document.getElementById('toLocation1').addEventListener('change', function() {
    document.getElementById('toLocationName1').value = this.options[this.selectedIndex].getAttribute('data-name') || '';
});
document.getElementById('toLocation2').addEventListener('change', function() {
    document.getElementById('toLocationName2').value = this.options[this.selectedIndex].getAttribute('data-name') || '';
});

function searchPatient() {
    var pid = document.getElementById('patientIdInput').value.trim();
    if (!pid) { alert('Please enter a Patient ID'); return; }

    var resultsDiv = document.getElementById('patientResults');
    resultsDiv.className = '';
    resultsDiv.innerHTML = '<div class="xf-loading">Searching...</div>';

    var xhr = new XMLHttpRequest();
    xhr.open('GET', 'SampleTransfer.do?searchAction=searchPatient&patientId=' + encodeURIComponent(pid), true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                resultsDiv.innerHTML = xhr.responseText;
                var hasSamples = resultsDiv.querySelector('input[name="sampleIds"]');
                if (hasSamples) {
                    document.getElementById('orderTransferSection').className = '';
                    document.getElementById('patientIdOrderHidden').value = pid;
                } else {
                    document.getElementById('orderTransferSection').className = 'xf-hidden';
                }
            } else {
                resultsDiv.innerHTML = '<div class="xf-msg xf-msg-error">Search failed. Please try again.</div>';
            }
        }
    };
    xhr.send();
}

function confirmOrderTransfer() {
    var checked = document.querySelectorAll('input[name="sampleIds"]:checked');
    if (checked.length === 0) {
        alert('Please select at least one sample/order to transfer.');
        return false;
    }
    var loc = document.getElementById('toLocation2');
    var locName = loc.options[loc.selectedIndex] ? loc.options[loc.selectedIndex].text : '';
    return confirm('Transfer ' + checked.length + ' sample(s) to ' + locName + '?');
}

function toggleAllSamples(checkbox) {
    document.querySelectorAll('input.sample-checkbox').forEach(function(cb) {
        cb.checked = checkbox.checked;
    });
}
</script>
