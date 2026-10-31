<%@ page language="java" contentType="text/html; charset=utf-8"
    import="java.sql.*, java.util.*, java.net.*, java.io.*, org.json.*"%>
<%@ taglib uri="/tags/struts-bean" prefix="bean" %>
<%@ taglib uri="/tags/struts-html" prefix="html" %>
<%@ taglib uri="/tags/struts-logic" prefix="logic" %>

<style>
    #locTable { border-collapse: collapse; width: 100%; }
    #locTable th, #locTable td { border: 1px solid #ccc; padding: 6px 8px; text-align: left; }
    #locTable th { background: #486086; color: white; cursor: pointer; white-space: nowrap; font-size: 12px; }
    #locTable th:hover { background: #3a4f6f; }
    #locTable tr:nth-child(even) { background: #f9f9f9; }
    #locTable tr:hover { background: #e8f0fe; }
    .loc-btn { padding: 5px 12px; cursor: pointer; border: 1px solid #999; background: #f0f0f0; margin: 2px; font-size: 12px; border-radius: 4px; font-weight: 500; }
    .loc-btn-primary { background: #486086; color: white; border: none; }
    .loc-btn-danger { background: #c0392b; color: white; border: none; }
    .loc-btn-success { background: #27ae60; color: white; border: none; }
    .loc-btn-info { background: #0284c7; color: white; border: none; }
    .loc-btn-warning { background: #f39c12; color: white; border: none; }
    .loc-btn-sm { padding: 2px 7px; font-size: 11px; }
    .loc-status-y { color: #27ae60; font-weight: bold; }
    .loc-status-n { color: #888; }
    .loc-msg { padding: 8px 12px; border-radius: 4px; margin-bottom: 10px; font-weight: bold; }
    .loc-msg-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .loc-msg-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    .loc-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 999; display: flex; align-items: center; justify-content: center; }
    .loc-modal { background: white; border-radius: 8px; padding: 20px; width: 500px; max-height: 80vh; overflow-y: auto; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
    .loc-modal h3 { margin-top: 0; color: #486086; }
    .loc-form-row { display: flex; gap: 10px; margin-bottom: 10px; align-items: center; }
    .loc-form-row label { font-weight: bold; width: 120px; font-size: 13px; }
    .loc-form-row input, .loc-form-row textarea { flex: 1; padding: 5px 8px; font-size: 13px; border: 1px solid #ccc; border-radius: 3px; }
    .loc-form-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee; }
    
    .badge-matched { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    .badge-mismatch { background: #fff3cd; color: #856404; border: 1px solid #ffeeba; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    .badge-unlinked { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    .badge-retired { background: #e2e3e5; color: #383d41; border: 1px solid #d6d8db; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    
    .tab-btn { padding: 8px 16px; border: 1px solid #ccc; background: #f0f0f0; cursor: pointer; font-size: 13px; font-weight: 500; border-radius: 4px 4px 0 0; margin-right: 4px; }
    .tab-btn.active { background: #486086; color: white; border-bottom: 1px solid #486086; font-weight: bold; }
    .mono { font-family: Consolas, monospace; font-size: 11px; color: #555; }
</style>

<div style="margin-bottom:15px; display:flex; justify-content:space-between; align-items:center;">
    <a href="MasterListsPage.do" style="color:#486086;text-decoration:none;font-weight:bold;font-size:14px;">&#8592; Back to Master Lists</a>
    <div style="display:flex; gap:8px;">
        <form method="POST" action="LabLocationAdmin.do" style="margin:0;">
            <input type="hidden" name="action" value="harmonize_openmrs">
            <button type="submit" class="loc-btn loc-btn-info" style="font-weight:bold;">
                🔄 Harmonize with OpenMRS
            </button>
        </form>
        <form method="POST" action="LabLocationAdmin.do" style="margin:0;">
            <input type="hidden" name="action" value="match_all_names">
            <button type="submit" class="loc-btn loc-btn-warning" style="font-weight:bold;">
                ✨ Match All Names from OpenMRS
            </button>
        </form>
        <a href="http://localhost:8000" target="_blank" class="loc-btn loc-btn-success" style="text-decoration:none;display:inline-flex;align-items:center;gap:6px;font-weight:bold;">
            <span>⚡ Port 8000: Result Sync Service</span>
        </a>
    </div>
</div>

<%
    String dbUrl = "jdbc:postgresql://openelisdb:5432/clinlims";
    String dbUser = "clinlims";
    String dbPass = "clinlims";

    String action = request.getParameter("action") != null ? request.getParameter("action") : "";
    String viewMode = request.getParameter("view") != null ? request.getParameter("view") : "source";
    String msgType = "";
    String msgText = "";

    // 1. Fetch OpenMRS Locations for in-page display & comparison
    Map<String, String> omrsUuidToName = new HashMap<String, String>();
    Map<String, Boolean> omrsUuidToRetired = new HashMap<String, Boolean>();
    Map<String, String> omrsNameToUuid = new HashMap<String, String>();

    try {
        URL omrsUrl = new URL("http://openmrs:8080/openmrs/ws/rest/v1/location?v=custom:(uuid,name,retired)&limit=1000&includeAll=true");
        HttpURLConnection omrsConn = (HttpURLConnection) omrsUrl.openConnection();
        omrsConn.setRequestMethod("GET");
        String authStr = "admin:Admin123";
        String encAuthStr = java.util.Base64.getEncoder().encodeToString(authStr.getBytes("UTF-8"));
        omrsConn.setRequestProperty("Authorization", "Basic " + encAuthStr);
        omrsConn.setConnectTimeout(4000);
        omrsConn.setReadTimeout(4000);

        if (omrsConn.getResponseCode() == 200) {
            BufferedReader br = new BufferedReader(new InputStreamReader(omrsConn.getInputStream(), "UTF-8"));
            StringBuilder sb = new StringBuilder();
            String l;
            while ((l = br.readLine()) != null) sb.append(l);
            br.close();

            JSONObject oRes = new JSONObject(sb.toString());
            JSONArray locs = oRes.optJSONArray("results");
            if (locs != null) {
                for (int i = 0; i < locs.length(); i++) {
                    JSONObject o = locs.getJSONObject(i);
                    String u = o.optString("uuid", "").trim();
                    String n = o.optString("name", "").trim();
                    boolean ret = o.optBoolean("retired", false);
                    if (!u.isEmpty() && !n.isEmpty()) {
                        omrsUuidToName.put(u, n);
                        omrsUuidToRetired.put(u, ret);
                        omrsNameToUuid.put(n.toLowerCase(), u);
                    }
                }
            }
        }
    } catch (Exception ignore) {}

    // 2. Handle Harmonize with OpenMRS
    if ("harmonize_openmrs".equals(action)) {
        Connection hConn = null;
        try {
            Class.forName("org.postgresql.Driver");
            hConn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
            hConn.setAutoCommit(false);

            int srcAdded = 0;
            int srcUpdated = 0;
            int locAdded = 0;
            int locUpdated = 0;

            PreparedStatement chkRefStmt = hConn.prepareStatement(
                "SELECT item_id FROM external_reference WHERE external_id = ? AND type = 'SampleSource'");
            PreparedStatement chkSrcNameStmt = hConn.prepareStatement(
                "SELECT id FROM sample_source WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))");
            PreparedStatement updSrcStmt = hConn.prepareStatement(
                "UPDATE sample_source SET name = ?, description = ?, active = ? WHERE id = ?");
            PreparedStatement insSrcStmt = hConn.prepareStatement(
                "INSERT INTO sample_source (id, name, description, active, display_order) VALUES ((SELECT COALESCE(MAX(id),0)+1 FROM sample_source), ?, ?, ?, (SELECT COALESCE(MAX(display_order),0)+1 FROM sample_source)) RETURNING id");
            PreparedStatement insRefStmt = hConn.prepareStatement(
                "INSERT INTO external_reference (item_id, external_id, type) VALUES (?, ?, 'SampleSource')");

            PreparedStatement chkLocStmt = hConn.prepareStatement("SELECT id FROM lab_location WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))");
            PreparedStatement insLocStmt = hConn.prepareStatement(
                "INSERT INTO lab_location (name, description, is_active, created, updated) VALUES (?, ?, ?, NOW(), NOW())");
            PreparedStatement updLocStmt = hConn.prepareStatement(
                "UPDATE lab_location SET is_active = ?, updated = NOW() WHERE id = ?");

            for (Map.Entry<String, String> entry : omrsUuidToName.entrySet()) {
                String locUuid = entry.getKey();
                String locName = entry.getValue();
                boolean retired = Boolean.TRUE.equals(omrsUuidToRetired.get(locUuid));

                if (locName.isEmpty()) continue;

                // Harmonize sample_source
                chkRefStmt.setString(1, locUuid);
                ResultSet refRs = chkRefStmt.executeQuery();
                if (refRs.next()) {
                    int existingSrcId = refRs.getInt("item_id");
                    updSrcStmt.setString(1, locName);
                    updSrcStmt.setString(2, locName);
                    updSrcStmt.setBoolean(3, !retired);
                    updSrcStmt.setInt(4, existingSrcId);
                    updSrcStmt.executeUpdate();
                    srcUpdated++;
                } else {
                    chkSrcNameStmt.setString(1, locName);
                    ResultSet nameRs = chkSrcNameStmt.executeQuery();
                    if (nameRs.next()) {
                        int existingSrcId = nameRs.getInt("id");
                        updSrcStmt.setString(1, locName);
                        updSrcStmt.setString(2, locName);
                        updSrcStmt.setBoolean(3, !retired);
                        updSrcStmt.setInt(4, existingSrcId);
                        updSrcStmt.executeUpdate();

                        insRefStmt.setInt(1, existingSrcId);
                        insRefStmt.setString(2, locUuid);
                        insRefStmt.executeUpdate();
                        srcUpdated++;
                    } else {
                        insSrcStmt.setString(1, locName);
                        insSrcStmt.setString(2, locName);
                        insSrcStmt.setBoolean(3, !retired);
                        ResultSet newSrcRs = insSrcStmt.executeQuery();
                        if (newSrcRs.next()) {
                            int newSrcId = newSrcRs.getInt(1);
                            insRefStmt.setInt(1, newSrcId);
                            insRefStmt.setString(2, locUuid);
                            insRefStmt.executeUpdate();
                            srcAdded++;
                        }
                        newSrcRs.close();
                    }
                    nameRs.close();
                }
                refRs.close();

                // Harmonize lab_location
                chkLocStmt.setString(1, locName);
                ResultSet chkRs = chkLocStmt.executeQuery();
                if (chkRs.next()) {
                    int existingId = chkRs.getInt("id");
                    updLocStmt.setBoolean(1, !retired);
                    updLocStmt.setInt(2, existingId);
                    updLocStmt.executeUpdate();
                    locUpdated++;
                } else {
                    insLocStmt.setString(1, locName);
                    insLocStmt.setString(2, "OpenMRS Location: " + locName);
                    insLocStmt.setBoolean(3, !retired);
                    insLocStmt.executeUpdate();
                    locAdded++;
                }
                chkRs.close();
            }

            chkRefStmt.close();
            chkSrcNameStmt.close();
            updSrcStmt.close();
            insSrcStmt.close();
            insRefStmt.close();
            chkLocStmt.close();
            insLocStmt.close();
            updLocStmt.close();

            // Backfill unassigned samples
            PreparedStatement fixSamples = hConn.prepareStatement(
                "UPDATE sample SET lab_location_id = (SELECT id FROM lab_location WHERE name = 'Main Laboratory' LIMIT 1) WHERE lab_location_id IS NULL");
            int samplesFixed = fixSamples.executeUpdate();
            fixSamples.close();

            hConn.commit();
            msgType = "success";
            msgText = "Harmonization complete! Sources: " + srcAdded + " created, " + srcUpdated + " updated. Lab Locations: " + locAdded + " added, " + locUpdated + " updated.";
        } catch (Exception e) {
            msgType = "error";
            msgText = "Harmonization error: " + e.getMessage();
            if (hConn != null) try { hConn.rollback(); } catch (Exception rx) {}
        } finally {
            if (hConn != null) try { hConn.close(); } catch (Exception ex) {}
        }
    }
    // 3. Handle Match Single Name
    else if ("match_name".equals(action)) {
        String targetId = request.getParameter("targetId");
        String targetName = request.getParameter("targetName");
        if (targetId != null && targetName != null && !targetName.trim().isEmpty()) {
            Connection mConn = null;
            try {
                Class.forName("org.postgresql.Driver");
                mConn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
                PreparedStatement ps = mConn.prepareStatement("UPDATE sample_source SET name = ?, description = ? WHERE id = ?::int");
                ps.setString(1, targetName.trim());
                ps.setString(2, targetName.trim());
                ps.setString(3, targetId.trim());
                ps.executeUpdate();
                ps.close();
                msgType = "success";
                msgText = "Source #" + targetId + " name updated to match OpenMRS: \"" + targetName.trim() + "\"";
            } catch (Exception e) {
                msgType = "error";
                msgText = "Match name error: " + e.getMessage();
            } finally {
                if (mConn != null) try { mConn.close(); } catch (Exception ex) {}
            }
        }
    }
    // 4. Handle Match All Names
    else if ("match_all_names".equals(action)) {
        Connection maConn = null;
        try {
            Class.forName("org.postgresql.Driver");
            maConn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
            maConn.setAutoCommit(false);

            Statement qStmt = maConn.createStatement();
            ResultSet qRs = qStmt.executeQuery(
                "SELECT ss.id, ss.name, er.external_id FROM sample_source ss JOIN external_reference er ON ss.id = er.item_id AND er.type = 'SampleSource'");

            PreparedStatement updStmt = maConn.prepareStatement("UPDATE sample_source SET name = ?, description = ? WHERE id = ?");
            int matchedCount = 0;

            while (qRs.next()) {
                int sid = qRs.getInt("id");
                String currentName = qRs.getString("name");
                String uuid = qRs.getString("external_id");
                String omrsName = omrsUuidToName.get(uuid);

                if (omrsName != null && !omrsName.trim().isEmpty() && !omrsName.trim().equals(currentName.trim())) {
                    updStmt.setString(1, omrsName.trim());
                    updStmt.setString(2, omrsName.trim());
                    updStmt.setInt(3, sid);
                    updStmt.executeUpdate();
                    matchedCount++;
                }
            }
            updStmt.close();
            qRs.close();
            qStmt.close();
            maConn.commit();

            msgType = "success";
            msgText = "Matched " + matchedCount + " source name(s) to exact OpenMRS location names!";
        } catch (Exception e) {
            msgType = "error";
            msgText = "Match all names error: " + e.getMessage();
            if (maConn != null) try { maConn.rollback(); } catch (Exception rx) {}
        } finally {
            if (maConn != null) try { maConn.close(); } catch (Exception ex) {}
        }
    }
    // 5. Handle Toggle Active
    else if ("toggle_active".equals(action)) {
        String targetId = request.getParameter("targetId");
        if (targetId != null && !targetId.isEmpty()) {
            Connection tConn = null;
            try {
                Class.forName("org.postgresql.Driver");
                tConn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
                if ("source".equals(viewMode)) {
                    PreparedStatement ps = tConn.prepareStatement("UPDATE sample_source SET active = NOT active WHERE id = ?::int");
                    ps.setString(1, targetId);
                    ps.executeUpdate();
                    ps.close();
                } else {
                    PreparedStatement ps = tConn.prepareStatement("UPDATE lab_location SET is_active = NOT is_active, updated = NOW() WHERE id = ?::int");
                    ps.setString(1, targetId);
                    ps.executeUpdate();
                    ps.close();
                }
                msgType = "success";
                msgText = "Status toggled successfully.";
            } catch (Exception e) {
                msgType = "error";
                msgText = "Toggle error: " + e.getMessage();
            } finally {
                if (tConn != null) try { tConn.close(); } catch (Exception ex) {}
            }
        }
    }
    // 6. Handle Delete Single Source
    else if ("delete_source".equals(action)) {
        String targetId = request.getParameter("targetId");
        if (targetId != null && !targetId.trim().isEmpty()) {
            Connection dConn = null;
            try {
                Class.forName("org.postgresql.Driver");
                dConn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
                dConn.setAutoCommit(false);
                int sid = Integer.parseInt(targetId.trim());

                String srcName = "";
                String locUuid = null;
                PreparedStatement qInfo = dConn.prepareStatement(
                    "SELECT ss.name, er.external_id FROM sample_source ss LEFT JOIN external_reference er ON ss.id = er.item_id AND er.type = 'SampleSource' WHERE ss.id = ?");
                qInfo.setInt(1, sid);
                ResultSet infoRs = qInfo.executeQuery();
                if (infoRs.next()) {
                    srcName = infoRs.getString("name");
                    locUuid = infoRs.getString("external_id");
                }
                infoRs.close();
                qInfo.close();

                PreparedStatement uSample = dConn.prepareStatement("UPDATE sample SET sample_source_id = NULL WHERE sample_source_id = ?");
                uSample.setInt(1, sid);
                uSample.executeUpdate();
                uSample.close();

                PreparedStatement dRef = dConn.prepareStatement("DELETE FROM external_reference WHERE item_id = ? AND type = 'SampleSource'");
                dRef.setInt(1, sid);
                dRef.executeUpdate();
                dRef.close();

                PreparedStatement dSrc = dConn.prepareStatement("DELETE FROM sample_source WHERE id = ?");
                dSrc.setInt(1, sid);
                int deleted = dSrc.executeUpdate();
                dSrc.close();

                // If linked to OpenMRS, attempt delete/retire in OpenMRS
                if (locUuid != null && !locUuid.trim().isEmpty()) {
                    try {
                        URL delUrl = new URL("http://openmrs:8080/openmrs/ws/rest/v1/location/" + locUuid.trim() + "?purge=true");
                        HttpURLConnection delConn = (HttpURLConnection) delUrl.openConnection();
                        delConn.setRequestMethod("DELETE");
                        String auth = "Basic " + java.util.Base64.getEncoder().encodeToString("admin:Admin123".getBytes("UTF-8"));
                        delConn.setRequestProperty("Authorization", auth);
                        delConn.setConnectTimeout(3000);
                        delConn.setReadTimeout(3000);
                        int rCode = delConn.getResponseCode();
                        if (rCode != 200 && rCode != 204) {
                            URL retUrl = new URL("http://openmrs:8080/openmrs/ws/rest/v1/location/" + locUuid.trim() + "?reason=deleted_by_admin");
                            HttpURLConnection retConn = (HttpURLConnection) retUrl.openConnection();
                            retConn.setRequestMethod("DELETE");
                            retConn.setRequestProperty("Authorization", auth);
                            retConn.getResponseCode();
                        }
                    } catch (Exception omrsEx) {}
                }

                dConn.commit();
                msgType = "success";
                msgText = "Source #" + sid + " (\"" + (srcName != null ? srcName : "") + "\") deleted successfully.";
            } catch (Exception e) {
                msgType = "error";
                msgText = "Delete error: " + e.getMessage();
                if (dConn != null) try { dConn.rollback(); } catch (Exception rx) {}
            } finally {
                if (dConn != null) try { dConn.close(); } catch (Exception ex) {}
            }
        }
    }
    // 7. Handle Save / Edit Sample Source
    else if ("save_source".equals(action)) {
        String mId = request.getParameter("modalId");
        String mName = request.getParameter("modalName");
        String mDesc = request.getParameter("modalDesc");
        String mUuid = request.getParameter("modalUuid");
        boolean mActive = "true".equalsIgnoreCase(request.getParameter("modalActive"));

        if (mName != null && !mName.trim().isEmpty()) {
            Connection sConn = null;
            try {
                Class.forName("org.postgresql.Driver");
                sConn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
                sConn.setAutoCommit(false);

                if (mId == null || mId.trim().isEmpty()) {
                    PreparedStatement ins = sConn.prepareStatement(
                        "INSERT INTO sample_source (id, name, description, active, display_order) VALUES ((SELECT COALESCE(MAX(id),0)+1 FROM sample_source), ?, ?, ?, (SELECT COALESCE(MAX(display_order),0)+1 FROM sample_source)) RETURNING id");
                    ins.setString(1, mName.trim());
                    ins.setString(2, mDesc != null ? mDesc.trim() : mName.trim());
                    ins.setBoolean(3, mActive);
                    ResultSet nRs = ins.executeQuery();
                    int newId = 0;
                    if (nRs.next()) newId = nRs.getInt(1);
                    nRs.close();
                    ins.close();

                    if (newId > 0 && mUuid != null && !mUuid.trim().isEmpty()) {
                        PreparedStatement insRef = sConn.prepareStatement(
                            "INSERT INTO external_reference (item_id, external_id, type) VALUES (?, ?, 'SampleSource')");
                        insRef.setInt(1, newId);
                        insRef.setString(2, mUuid.trim());
                        insRef.executeUpdate();
                        insRef.close();
                    }
                    msgType = "success";
                    msgText = "Source \"" + mName.trim() + "\" created successfully.";
                } else {
                    int sid = Integer.parseInt(mId.trim());
                    PreparedStatement upd = sConn.prepareStatement(
                        "UPDATE sample_source SET name = ?, description = ?, active = ? WHERE id = ?");
                    upd.setString(1, mName.trim());
                    upd.setString(2, mDesc != null ? mDesc.trim() : "");
                    upd.setBoolean(3, mActive);
                    upd.setInt(4, sid);
                    upd.executeUpdate();
                    upd.close();

                    if (mUuid != null && !mUuid.trim().isEmpty()) {
                        PreparedStatement chkRef = sConn.prepareStatement(
                            "SELECT id FROM external_reference WHERE item_id = ? AND type = 'SampleSource'");
                        chkRef.setInt(1, sid);
                        ResultSet crRs = chkRef.executeQuery();
                        if (crRs.next()) {
                            PreparedStatement updRef = sConn.prepareStatement(
                                "UPDATE external_reference SET external_id = ? WHERE item_id = ? AND type = 'SampleSource'");
                            updRef.setString(1, mUuid.trim());
                            updRef.setInt(2, sid);
                            updRef.executeUpdate();
                            updRef.close();
                        } else {
                            PreparedStatement insRef = sConn.prepareStatement(
                                "INSERT INTO external_reference (item_id, external_id, type) VALUES (?, ?, 'SampleSource')");
                            insRef.setInt(1, sid);
                            insRef.setString(2, mUuid.trim());
                            insRef.executeUpdate();
                            insRef.close();
                        }
                        crRs.close();
                        chkRef.close();
                    } else {
                        PreparedStatement delRef = sConn.prepareStatement(
                            "DELETE FROM external_reference WHERE item_id = ? AND type = 'SampleSource'");
                        delRef.setInt(1, sid);
                        delRef.executeUpdate();
                        delRef.close();
                    }
                    msgType = "success";
                    msgText = "Source #" + sid + " (\"" + mName.trim() + "\") updated successfully.";
                }
                sConn.commit();
            } catch (Exception e) {
                msgType = "error";
                msgText = "Save source error: " + e.getMessage();
                if (sConn != null) try { sConn.rollback(); } catch (Exception rx) {}
            } finally {
                if (sConn != null) try { sConn.close(); } catch (Exception ex) {}
            }
        }
    }
    // 8. Handle Save / Edit Lab Location (Bench)
    else if ("save_location".equals(action)) {
        String mId = request.getParameter("modalId");
        String mName = request.getParameter("modalName");
        String mDesc = request.getParameter("modalDesc");
        String mAddr = request.getParameter("modalAddr");
        String mPhone = request.getParameter("modalPhone");
        boolean mActive = "true".equalsIgnoreCase(request.getParameter("modalActive"));

        if (mName != null && !mName.trim().isEmpty()) {
            Connection lConn = null;
            try {
                Class.forName("org.postgresql.Driver");
                lConn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
                lConn.setAutoCommit(false);

                if (mId == null || mId.trim().isEmpty()) {
                    PreparedStatement ins = lConn.prepareStatement(
                        "INSERT INTO lab_location (name, description, address, phone, is_active, created, updated) VALUES (?, ?, ?, ?, ?, NOW(), NOW())");
                    ins.setString(1, mName.trim());
                    ins.setString(2, mDesc != null ? mDesc.trim() : "");
                    ins.setString(3, mAddr != null ? mAddr.trim() : "");
                    ins.setString(4, mPhone != null ? mPhone.trim() : "");
                    ins.setBoolean(5, mActive);
                    ins.executeUpdate();
                    ins.close();
                    msgType = "success";
                    msgText = "Lab Location \"" + mName.trim() + "\" created successfully.";
                } else {
                    int lid = Integer.parseInt(mId.trim());
                    PreparedStatement upd = lConn.prepareStatement(
                        "UPDATE lab_location SET name = ?, description = ?, address = ?, phone = ?, is_active = ?, updated = NOW() WHERE id = ?");
                    upd.setString(1, mName.trim());
                    upd.setString(2, mDesc != null ? mDesc.trim() : "");
                    upd.setString(3, mAddr != null ? mAddr.trim() : "");
                    upd.setString(4, mPhone != null ? mPhone.trim() : "");
                    upd.setBoolean(5, mActive);
                    upd.setInt(6, lid);
                    upd.executeUpdate();
                    upd.close();
                    msgType = "success";
                    msgText = "Lab Location #" + lid + " (\"" + mName.trim() + "\") updated successfully.";
                }
                lConn.commit();
            } catch (Exception e) {
                msgType = "error";
                msgText = "Save location error: " + e.getMessage();
                if (lConn != null) try { lConn.rollback(); } catch (Exception rx) {}
            } finally {
                if (lConn != null) try { lConn.close(); } catch (Exception ex) {}
            }
        }
    }
    // 9. Handle Batch Toggle Active
    else if ("batch_toggle".equals(action)) {
        String targetIds = request.getParameter("targetIds");
        if (targetIds != null && !targetIds.trim().isEmpty()) {
            Connection btConn = null;
            try {
                Class.forName("org.postgresql.Driver");
                btConn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
                btConn.setAutoCommit(false);
                String[] idArr = targetIds.split(",");
                int toggledCount = 0;

                if ("source".equals(viewMode)) {
                    PreparedStatement ps = btConn.prepareStatement("UPDATE sample_source SET active = NOT active WHERE id = ?");
                    for (String rid : idArr) {
                        rid = rid.trim();
                        if (rid.isEmpty()) continue;
                        ps.setInt(1, Integer.parseInt(rid));
                        ps.executeUpdate();
                        toggledCount++;
                    }
                    ps.close();
                } else {
                    PreparedStatement ps = btConn.prepareStatement("UPDATE lab_location SET is_active = NOT is_active, updated = NOW() WHERE id = ?");
                    for (String rid : idArr) {
                        rid = rid.trim();
                        if (rid.isEmpty()) continue;
                        ps.setInt(1, Integer.parseInt(rid));
                        ps.executeUpdate();
                        toggledCount++;
                    }
                    ps.close();
                }
                btConn.commit();
                msgType = "success";
                msgText = "Successfully toggled status for " + toggledCount + " item(s).";
            } catch (Exception e) {
                msgType = "error";
                msgText = "Batch toggle error: " + e.getMessage();
                if (btConn != null) try { btConn.rollback(); } catch (Exception rx) {}
            } finally {
                if (btConn != null) try { btConn.close(); } catch (Exception ex) {}
            }
        }
    }
    // 10. Handle Batch Delete
    else if ("delete_batch".equals(action)) {
        String targetIds = request.getParameter("targetIds");
        if (targetIds != null && !targetIds.trim().isEmpty()) {
            Connection bConn = null;
            try {
                Class.forName("org.postgresql.Driver");
                bConn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
                bConn.setAutoCommit(false);

                String[] idArr = targetIds.split(",");
                int delCount = 0;

                if ("source".equals(viewMode)) {
                    PreparedStatement qInfo = bConn.prepareStatement(
                        "SELECT ss.name, er.external_id FROM sample_source ss LEFT JOIN external_reference er ON ss.id = er.item_id AND er.type = 'SampleSource' WHERE ss.id = ?");
                    PreparedStatement uSample = bConn.prepareStatement("UPDATE sample SET sample_source_id = NULL WHERE sample_source_id = ?");
                    PreparedStatement dRef = bConn.prepareStatement("DELETE FROM external_reference WHERE item_id = ? AND type = 'SampleSource'");
                    PreparedStatement dSrc = bConn.prepareStatement("DELETE FROM sample_source WHERE id = ?");

                    String auth = "Basic " + java.util.Base64.getEncoder().encodeToString("admin:Admin123".getBytes("UTF-8"));

                    for (String rawId : idArr) {
                        rawId = rawId.trim();
                        if (rawId.isEmpty()) continue;
                        try {
                            int sid = Integer.parseInt(rawId);

                            String locUuid = null;
                            qInfo.setInt(1, sid);
                            ResultSet infoRs = qInfo.executeQuery();
                            if (infoRs.next()) {
                                locUuid = infoRs.getString("external_id");
                            }
                            infoRs.close();

                            uSample.setInt(1, sid);
                            uSample.executeUpdate();

                            dRef.setInt(1, sid);
                            dRef.executeUpdate();

                            dSrc.setInt(1, sid);
                            int dRes = dSrc.executeUpdate();
                            if (dRes > 0) delCount++;

                            if (locUuid != null && !locUuid.trim().isEmpty()) {
                                try {
                                    URL delUrl = new URL("http://openmrs:8080/openmrs/ws/rest/v1/location/" + locUuid.trim() + "?purge=true");
                                    HttpURLConnection delConn = (HttpURLConnection) delUrl.openConnection();
                                    delConn.setRequestMethod("DELETE");
                                    delConn.setRequestProperty("Authorization", auth);
                                    delConn.setConnectTimeout(3000);
                                    delConn.setReadTimeout(3000);
                                    int rCode = delConn.getResponseCode();
                                    if (rCode != 200 && rCode != 204) {
                                        URL retUrl = new URL("http://openmrs:8080/openmrs/ws/rest/v1/location/" + locUuid.trim() + "?reason=deleted_by_admin");
                                        HttpURLConnection retConn = (HttpURLConnection) retUrl.openConnection();
                                        retConn.setRequestMethod("DELETE");
                                        retConn.setRequestProperty("Authorization", auth);
                                        retConn.getResponseCode();
                                    }
                                } catch (Exception ignoreOmrs) {}
                            }
                        } catch (Exception itemEx) {}
                    }
                    qInfo.close();
                    uSample.close();
                    dRef.close();
                    dSrc.close();
                } else {
                    PreparedStatement uSamp = bConn.prepareStatement(
                        "UPDATE sample SET lab_location_id = (SELECT id FROM lab_location WHERE name = 'Main Laboratory' LIMIT 1) WHERE lab_location_id = ?");
                    PreparedStatement uFrom = bConn.prepareStatement("UPDATE sample_transfer SET from_location_id = NULL WHERE from_location_id = ?");
                    PreparedStatement uTo = bConn.prepareStatement("UPDATE sample_transfer SET to_location_id = NULL WHERE to_location_id = ?");
                    PreparedStatement uUsr = bConn.prepareStatement("UPDATE system_user SET default_lab_location_id = NULL WHERE default_lab_location_id = ?");
                    PreparedStatement uTst = bConn.prepareStatement("UPDATE test SET lab_location_id = NULL WHERE lab_location_id = ?");
                    PreparedStatement dLoc = bConn.prepareStatement("DELETE FROM lab_location WHERE id = ?");

                    for (String rawId : idArr) {
                        rawId = rawId.trim();
                        if (rawId.isEmpty()) continue;
                        try {
                            int lid = Integer.parseInt(rawId);
                            uSamp.setInt(1, lid); uSamp.executeUpdate();
                            uFrom.setInt(1, lid); uFrom.executeUpdate();
                            uTo.setInt(1, lid); uTo.executeUpdate();
                            uUsr.setInt(1, lid); uUsr.executeUpdate();
                            uTst.setInt(1, lid); uTst.executeUpdate();
                            dLoc.setInt(1, lid);
                            if (dLoc.executeUpdate() > 0) delCount++;
                        } catch (Exception ignoreL) {}
                    }
                    uSamp.close(); uFrom.close(); uTo.close(); uUsr.close(); uTst.close(); dLoc.close();
                }

                bConn.commit();
                msgType = "success";
                msgText = "Successfully deleted " + delCount + " item(s).";
            } catch (Exception e) {
                msgType = "error";
                msgText = "Batch delete error: " + e.getMessage();
                if (bConn != null) try { bConn.rollback(); } catch (Exception rx) {}
            } finally {
                if (bConn != null) try { bConn.close(); } catch (Exception ex) {}
            }
        }
    }
    // 11. Handle Delete Lab Location (Bench)
    else if ("delete_location".equals(action)) {
        String targetId = request.getParameter("targetId");
        if (targetId != null && !targetId.trim().isEmpty()) {
            Connection dlConn = null;
            try {
                Class.forName("org.postgresql.Driver");
                dlConn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
                dlConn.setAutoCommit(false);
                int lid = Integer.parseInt(targetId.trim());

                PreparedStatement uSamp = dlConn.prepareStatement(
                    "UPDATE sample SET lab_location_id = (SELECT id FROM lab_location WHERE name = 'Main Laboratory' LIMIT 1) WHERE lab_location_id = ?");
                uSamp.setInt(1, lid);
                uSamp.executeUpdate();
                uSamp.close();

                PreparedStatement uFrom = dlConn.prepareStatement("UPDATE sample_transfer SET from_location_id = NULL WHERE from_location_id = ?");
                uFrom.setInt(1, lid);
                uFrom.executeUpdate();
                uFrom.close();

                PreparedStatement uTo = dlConn.prepareStatement("UPDATE sample_transfer SET to_location_id = NULL WHERE to_location_id = ?");
                uTo.setInt(1, lid);
                uTo.executeUpdate();
                uTo.close();

                PreparedStatement uUsr = dlConn.prepareStatement("UPDATE system_user SET default_lab_location_id = NULL WHERE default_lab_location_id = ?");
                uUsr.setInt(1, lid);
                uUsr.executeUpdate();
                uUsr.close();

                PreparedStatement uTst = dlConn.prepareStatement("UPDATE test SET lab_location_id = NULL WHERE lab_location_id = ?");
                uTst.setInt(1, lid);
                uTst.executeUpdate();
                uTst.close();

                PreparedStatement dLoc = dlConn.prepareStatement("DELETE FROM lab_location WHERE id = ?");
                dLoc.setInt(1, lid);
                dLoc.executeUpdate();
                dLoc.close();

                dlConn.commit();
                msgType = "success";
                msgText = "Lab location #" + lid + " deleted successfully.";
            } catch (Exception e) {
                msgType = "error";
                msgText = "Delete location error: " + e.getMessage();
                if (dlConn != null) try { dlConn.rollback(); } catch (Exception rx) {}
            } finally {
                if (dlConn != null) try { dlConn.close(); } catch (Exception ex) {}
            }
        }
    }
%>

<% if (!msgText.isEmpty()) { %>
<div class="loc-msg loc-msg-<%= msgType %>"><%= msgText %></div>
<% } %>

<h2 style="text-align:center; margin-bottom:5px;">OpenMRS Location &amp; OpenELIS Source Harmonization</h2>
<p style="text-align:center; color:#555; margin-top:0; font-size:13px; margin-bottom:15px;">
    Harmonize OpenMRS Encounter Locations with OpenELIS Sample Sources to ensure all lab sample origins match accurately.
</p>

<!-- View Selector Tabs -->
<div style="display:flex; justify-content:space-between; align-items:flex-end; border-bottom:2px solid #486086; margin-bottom:12px;">
    <div style="display:flex;">
        <a href="LabLocationAdmin.do?view=source" class="tab-btn <%= "source".equals(viewMode) ? "active" : "" %>" style="text-decoration:none;">
            📍 OpenELIS Sample Sources (OpenMRS Locations)
        </a>
        <a href="LabLocationAdmin.do?view=location" class="tab-btn <%= "location".equals(viewMode) ? "active" : "" %>" style="text-decoration:none;">
            🔬 Internal Lab Locations (Benches)
        </a>
    </div>
</div>

<!-- Edit / Add Modal Overlay -->
<div id="locModalOverlay" class="loc-overlay" style="display:none;" onclick="if(event.target===this) closeEditModal();">
    <div class="loc-modal">
        <h3 id="modalTitle" style="margin-top:0; color:#486086;">Edit Item</h3>
        <form method="POST" action="LabLocationAdmin.do" id="locEditForm">
            <input type="hidden" name="action" id="modalAction" value="<%= "source".equals(viewMode) ? "save_source" : "save_location" %>">
            <input type="hidden" name="view" value="<%= viewMode %>">
            <input type="hidden" name="modalId" id="modalId" value="">

            <div class="loc-form-row">
                <label>Name: <span style="color:red;">*</span></label>
                <input type="text" name="modalName" id="modalName" required maxlength="<%= "source".equals(viewMode) ? "50" : "100" %>">
            </div>

            <div class="loc-form-row">
                <label>Description:</label>
                <input type="text" name="modalDesc" id="modalDesc" maxlength="<%= "source".equals(viewMode) ? "50" : "255" %>">
            </div>

            <% if ("source".equals(viewMode)) { %>
            <div class="loc-form-row">
                <label>OpenMRS UUID:</label>
                <input type="text" name="modalUuid" id="modalUuid" placeholder="e.g. 24ed3523-f2f0-44b9-94c0-c2f8f419175c (optional)">
            </div>
            <% } else { %>
            <div class="loc-form-row">
                <label>Address:</label>
                <input type="text" name="modalAddr" id="modalAddr" maxlength="255">
            </div>
            <div class="loc-form-row">
                <label>Phone:</label>
                <input type="text" name="modalPhone" id="modalPhone" maxlength="50">
            </div>
            <% } %>

            <div class="loc-form-row">
                <label>Status:</label>
                <select name="modalActive" id="modalActive" style="flex:1; padding:5px 8px; font-size:13px; border:1px solid #ccc; border-radius:3px;">
                    <option value="true">Active</option>
                    <option value="false">Retired / Inactive</option>
                </select>
            </div>

            <div class="loc-form-actions">
                <button type="button" class="loc-btn" onclick="closeEditModal()">Cancel</button>
                <button type="submit" class="loc-btn loc-btn-success" style="font-weight:bold;">Save Changes</button>
            </div>
        </form>
    </div>
</div>

<!-- Hidden form for batch actions -->
<form id="batchActionForm" method="POST" action="LabLocationAdmin.do" style="display:none;">
    <input type="hidden" name="action" id="batchActionInput" value="">
    <input type="hidden" name="view" value="<%= viewMode %>">
    <input type="hidden" name="targetIds" id="batchTargetIds" value="">
</form>

<%
    Connection qConn = null;
    int totalCount = 0;
    try {
        Class.forName("org.postgresql.Driver");
        qConn = DriverManager.getConnection(dbUrl, dbUser, dbPass);

        if ("source".equals(viewMode)) {
            Statement sStmt = qConn.createStatement();
            ResultSet sRs = sStmt.executeQuery(
                "SELECT ss.id, ss.name, ss.description, ss.active, er.external_id as uuid " +
                "FROM sample_source ss " +
                "LEFT JOIN external_reference er ON ss.id = er.item_id AND er.type = 'SampleSource' " +
                "ORDER BY ss.active DESC, ss.name ASC");
%>

<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; flex-wrap:wrap; gap:8px;">
    <div style="display:flex; gap:6px; align-items:center; flex-wrap:wrap;">
        <input type="text" id="filterInput" placeholder="🔍 Filter sources by name, OpenMRS name, UUID, ID..." 
               style="width:280px; padding:6px 10px; font-size:13px; border:1px solid #ccc; border-radius:4px;" 
               oninput="filterTable()">
        <button type="button" class="loc-btn loc-btn-sm" onclick="selectAllVisible()">Select All</button>
        <button type="button" class="loc-btn loc-btn-sm" onclick="deselectAll()">Deselect All</button>
        <button type="button" id="toggleSelectedBtn" class="loc-btn loc-btn-warning loc-btn-sm" 
                style="font-weight:bold; opacity:0.6;" disabled onclick="submitBatchAction('batch_toggle')">
            ⚡ Toggle Selected (0)
        </button>
        <button type="button" id="deleteSelectedBtn" class="loc-btn loc-btn-danger loc-btn-sm" 
                style="font-weight:bold; opacity:0.6;" disabled onclick="submitBatchAction('delete_batch')">
            🗑 Delete Selected (0)
        </button>
        <button type="button" class="loc-btn loc-btn-success loc-btn-sm" style="font-weight:bold;" onclick="openAddModal()">
            + Add Source
        </button>
    </div>
    <div>
        <span style="font-size:12px; color:#555;">Filter: </span>
        <button class="loc-btn loc-btn-sm" onclick="filterByMatch('ALL')">All</button>
        <button class="loc-btn loc-btn-sm" style="color:#27ae60;" onclick="filterByMatch('Matched')">🟢 Matched</button>
        <button class="loc-btn loc-btn-sm" style="color:#856404;" onclick="filterByMatch('Mismatch')">🟡 Mismatch</button>
        <button class="loc-btn loc-btn-sm" style="color:#721c24;" onclick="filterByMatch('Unlinked')">⚪ Unlinked</button>
        <button class="loc-btn loc-btn-sm" style="color:#6c757d;" onclick="filterByMatch('Retired')">⚫ Retired</button>
    </div>
</div>

<table id="locTable">
    <thead>
        <tr>
            <th style="width:30px; text-align:center;"><input type="checkbox" id="selectAllHeader" onclick="toggleSelectAll(this)"></th>
            <th style="width:35px;">ID</th>
            <th>OpenELIS Source Name</th>
            <th>OpenMRS Location Name</th>
            <th>OpenMRS UUID</th>
            <th style="width:110px;">Match Status</th>
            <th style="width:110px;">Status</th>
            <th style="width:180px; text-align:center;">Actions</th>
        </tr>
    </thead>
    <tbody id="locTableBody">
        <%
            while (sRs.next()) {
                totalCount++;
                int id = sRs.getInt("id");
                String name = sRs.getString("name");
                String desc = sRs.getString("description");
                boolean active = sRs.getBoolean("active");
                String uuid = sRs.getString("uuid");

                String activeClass = active ? "loc-status-y" : "loc-status-n";
                String activeText = active ? "Active" : "Retired";

                String omrsName = (uuid != null && !uuid.isEmpty()) ? omrsUuidToName.get(uuid) : null;
                boolean isRetiredInOmrs = (uuid != null && Boolean.TRUE.equals(omrsUuidToRetired.get(uuid)));

                String matchStatusClass = "";
                String matchStatusText = "";
                boolean isMismatch = false;

                if (uuid == null || uuid.isEmpty()) {
                    matchStatusClass = "badge-unlinked";
                    matchStatusText = "Unlinked";
                } else if (omrsName != null) {
                    if (isRetiredInOmrs) {
                        matchStatusClass = "badge-retired";
                        matchStatusText = "Retired in OpenMRS";
                    } else if (omrsName.trim().equalsIgnoreCase(name != null ? name.trim() : "")) {
                        matchStatusClass = "badge-matched";
                        matchStatusText = "Matched";
                    } else {
                        matchStatusClass = "badge-mismatch";
                        matchStatusText = "Name Mismatch";
                        isMismatch = true;
                    }
                } else {
                    matchStatusClass = "badge-retired";
                    matchStatusText = "Not in OpenMRS";
                }

                String safeOmrsName = omrsName != null ? omrsName.replace("'", "\\'").replace("\"", "&quot;") : "";
                String safeName = name != null ? name.replace("'", "\\'").replace("\"", "&quot;") : "";
                String safeDesc = desc != null ? desc.replace("'", "\\'").replace("\"", "&quot;") : "";
                String safeUuid = uuid != null ? uuid.replace("'", "\\'").replace("\"", "&quot;") : "";
        %>
        <tr data-match="<%= matchStatusText %>" data-status="<%= active ? "Active" : "Retired" %>">
            <td style="text-align:center;">
                <input type="checkbox" class="loc-check" value="<%= id %>" onchange="updateSelectedCount()">
            </td>
            <td><strong>#<%= id %></strong></td>
            <td><strong><%= name != null ? name : "" %></strong></td>
            <td>
                <% if (omrsName != null) { %>
                    <span style="<%= isMismatch ? "color:#856404; font-weight:bold; background:#fff3cd; padding:2px 6px; border-radius:3px;" : "color:#155724;" %>">
                        <%= omrsName %>
                    </span>
                <% } else { %>
                    <span style="color:#888; font-style:italic;">— Not in OpenMRS —</span>
                <% } %>
            </td>
            <td><%= uuid != null ? "<span class='mono'>" + uuid + "</span>" : "<span style='color:#999; font-style:italic;'>Unlinked</span>" %></td>
            <td><span class="<%= matchStatusClass %>"><%= matchStatusText %></span></td>
            <td>
                <span class="<%= activeClass %>"><%= activeText %></span>
                <form method="POST" action="LabLocationAdmin.do" style="display:inline; margin-left:4px;">
                    <input type="hidden" name="action" value="toggle_active">
                    <input type="hidden" name="view" value="source">
                    <input type="hidden" name="targetId" value="<%= id %>">
                    <button type="submit" class="loc-btn loc-btn-sm" title="Toggle active status">Toggle</button>
                </form>
            </td>
            <td style="text-align:center; white-space:nowrap;">
                <% if (isMismatch) { %>
                    <form method="POST" action="LabLocationAdmin.do" style="display:inline; margin-right:2px;">
                        <input type="hidden" name="action" value="match_name">
                        <input type="hidden" name="view" value="source">
                        <input type="hidden" name="targetId" value="<%= id %>">
                        <input type="hidden" name="targetName" value="<%= safeOmrsName %>">
                        <button type="submit" class="loc-btn loc-btn-warning loc-btn-sm" title="Update source name to match OpenMRS">
                            Match
                        </button>
                    </form>
                <% } %>
                <button type="button" class="loc-btn loc-btn-info loc-btn-sm" 
                        onclick="openEditSourceModal('<%= id %>', '<%= safeName %>', '<%= safeDesc %>', '<%= safeUuid %>', <%= active %>)" 
                        title="Edit source details">
                    Edit
                </button>
                <form method="POST" action="LabLocationAdmin.do" style="display:inline; margin-left:2px;" 
                      onsubmit="return confirm('Are you sure you want to delete source #<%= id %> (<%= safeName %>)?');">
                    <input type="hidden" name="action" value="delete_source">
                    <input type="hidden" name="view" value="source">
                    <input type="hidden" name="targetId" value="<%= id %>">
                    <button type="submit" class="loc-btn loc-btn-danger loc-btn-sm" title="Delete this source">
                        Delete
                    </button>
                </form>
            </td>
        </tr>
        <%
            }
            sRs.close();
            sStmt.close();
        %>
    </tbody>
</table>

<%
        } else {
            // Lab location (Bench) view
            Statement lStmt = qConn.createStatement();
            ResultSet lRs = lStmt.executeQuery("SELECT id, name, description, address, phone, is_active FROM lab_location ORDER BY is_active DESC, name ASC");
%>

<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; flex-wrap:wrap; gap:8px;">
    <div style="display:flex; gap:6px; align-items:center; flex-wrap:wrap;">
        <input type="text" id="filterInput" placeholder="🔍 Filter lab locations by name, description, phone..." 
               style="width:280px; padding:6px 10px; font-size:13px; border:1px solid #ccc; border-radius:4px;" 
               oninput="filterTable()">
        <button type="button" class="loc-btn loc-btn-sm" onclick="selectAllVisible()">Select All</button>
        <button type="button" class="loc-btn loc-btn-sm" onclick="deselectAll()">Deselect All</button>
        <button type="button" id="toggleSelectedBtn" class="loc-btn loc-btn-warning loc-btn-sm" 
                style="font-weight:bold; opacity:0.6;" disabled onclick="submitBatchAction('batch_toggle')">
            ⚡ Toggle Selected (0)
        </button>
        <button type="button" id="deleteSelectedBtn" class="loc-btn loc-btn-danger loc-btn-sm" 
                style="font-weight:bold; opacity:0.6;" disabled onclick="submitBatchAction('delete_batch')">
            🗑 Delete Selected (0)
        </button>
        <button type="button" class="loc-btn loc-btn-success loc-btn-sm" style="font-weight:bold;" onclick="openAddModal()">
            + Add Lab Location
        </button>
    </div>
    <div>
        <span style="font-size:12px; color:#555;">Filter: </span>
        <button class="loc-btn loc-btn-sm" onclick="filterByLocationStatus('ALL')">All</button>
        <button class="loc-btn loc-btn-sm" style="color:#27ae60;" onclick="filterByLocationStatus('Active')">🟢 Active</button>
        <button class="loc-btn loc-btn-sm" style="color:#721c24;" onclick="filterByLocationStatus('Inactive')">⚪ Inactive</button>
    </div>
</div>

<table id="locTable">
    <thead>
        <tr>
            <th style="width:30px; text-align:center;"><input type="checkbox" id="selectAllHeader" onclick="toggleSelectAll(this)"></th>
            <th style="width:35px;">ID</th>
            <th>Lab Location Name</th>
            <th>Description</th>
            <th>Address</th>
            <th>Phone</th>
            <th style="width:110px;">Status</th>
            <th style="width:140px; text-align:center;">Actions</th>
        </tr>
    </thead>
    <tbody id="locTableBody">
        <%
            while (lRs.next()) {
                totalCount++;
                int id = lRs.getInt("id");
                String name = lRs.getString("name");
                String desc = lRs.getString("description");
                String addr = lRs.getString("address");
                String phone = lRs.getString("phone");
                boolean active = lRs.getBoolean("is_active");

                String activeClass = active ? "loc-status-y" : "loc-status-n";
                String activeText = active ? "Active" : "Inactive";
                String safeName = name != null ? name.replace("'", "\\'").replace("\"", "&quot;") : "";
                String safeDesc = desc != null ? desc.replace("'", "\\'").replace("\"", "&quot;") : "";
                String safeAddr = addr != null ? addr.replace("'", "\\'").replace("\"", "&quot;") : "";
                String safePhone = phone != null ? phone.replace("'", "\\'").replace("\"", "&quot;") : "";
        %>
        <tr data-status="<%= active ? "Active" : "Inactive" %>">
            <td style="text-align:center;">
                <input type="checkbox" class="loc-check" value="<%= id %>" onchange="updateSelectedCount()">
            </td>
            <td><strong>#<%= id %></strong></td>
            <td><strong><%= name != null ? name : "" %></strong></td>
            <td><%= desc != null ? desc : "" %></td>
            <td><%= addr != null ? addr : "" %></td>
            <td><%= phone != null ? phone : "" %></td>
            <td>
                <span class="<%= activeClass %>"><%= activeText %></span>
                <form method="POST" action="LabLocationAdmin.do" style="display:inline; margin-left:4px;">
                    <input type="hidden" name="action" value="toggle_active">
                    <input type="hidden" name="view" value="location">
                    <input type="hidden" name="targetId" value="<%= id %>">
                    <button type="submit" class="loc-btn loc-btn-sm" title="Toggle active status">Toggle</button>
                </form>
            </td>
            <td style="text-align:center; white-space:nowrap;">
                <button type="button" class="loc-btn loc-btn-info loc-btn-sm" 
                        onclick="openEditLocationModal('<%= id %>', '<%= safeName %>', '<%= safeDesc %>', '<%= safeAddr %>', '<%= safePhone %>', <%= active %>)" 
                        title="Edit lab location details">
                    Edit
                </button>
                <form method="POST" action="LabLocationAdmin.do" style="display:inline; margin-left:2px;" 
                      onsubmit="return confirm('Are you sure you want to delete lab location #<%= id %> (<%= safeName %>)?');">
                    <input type="hidden" name="action" value="delete_location">
                    <input type="hidden" name="view" value="location">
                    <input type="hidden" name="targetId" value="<%= id %>">
                    <button type="submit" class="loc-btn loc-btn-danger loc-btn-sm" title="Delete this lab location">
                        Delete
                    </button>
                </form>
            </td>
        </tr>
        <%
            }
            lRs.close();
            lStmt.close();
        %>
    </tbody>
</table>

<%
        }
    } catch (Exception e) {
        out.println("<p style='color:red'>Database error: " + e.getMessage() + "</p>");
    } finally {
        if (qConn != null) try { qConn.close(); } catch (Exception ex) {}
    }
%>

<script>
function filterTable() {
    var q = (document.getElementById('filterInput').value || '').toLowerCase().trim();
    var rows = document.querySelectorAll('#locTableBody tr');
    for (var i = 0; i < rows.length; i++) {
        var text = rows[i].innerText.toLowerCase();
        rows[i].style.display = (text.indexOf(q) !== -1) ? '' : 'none';
    }
    updateSelectedCount();
}

function filterByMatch(status) {
    var rows = document.querySelectorAll('#locTableBody tr');
    for (var i = 0; i < rows.length; i++) {
        if (status === 'ALL') {
            rows[i].style.display = '';
        } else {
            var m = rows[i].getAttribute('data-match') || '';
            rows[i].style.display = (m.indexOf(status) !== -1) ? '' : 'none';
        }
    }
    updateSelectedCount();
}

function filterByLocationStatus(status) {
    var rows = document.querySelectorAll('#locTableBody tr');
    for (var i = 0; i < rows.length; i++) {
        if (status === 'ALL') {
            rows[i].style.display = '';
        } else {
            var st = rows[i].getAttribute('data-status') || '';
            rows[i].style.display = (st === status) ? '' : 'none';
        }
    }
    updateSelectedCount();
}

function toggleSelectAll(master) {
    var checks = document.querySelectorAll('.loc-check');
    for (var i = 0; i < checks.length; i++) {
        var row = checks[i].closest('tr');
        if (!row || row.style.display !== 'none') {
            checks[i].checked = master.checked;
        }
    }
    updateSelectedCount();
}

function selectAllVisible() {
    var checks = document.querySelectorAll('.loc-check');
    for (var i = 0; i < checks.length; i++) {
        var row = checks[i].closest('tr');
        if (!row || row.style.display !== 'none') {
            checks[i].checked = true;
        }
    }
    var h = document.getElementById('selectAllHeader');
    if (h) h.checked = true;
    updateSelectedCount();
}

function deselectAll() {
    var checks = document.querySelectorAll('.loc-check');
    for (var i = 0; i < checks.length; i++) {
        checks[i].checked = false;
    }
    var h = document.getElementById('selectAllHeader');
    if (h) h.checked = false;
    updateSelectedCount();
}

function updateSelectedCount() {
    var checked = document.querySelectorAll('.loc-check:checked');
    var delBtn = document.getElementById('deleteSelectedBtn');
    if (delBtn) {
        delBtn.innerText = '🗑 Delete Selected (' + checked.length + ')';
        delBtn.disabled = (checked.length === 0);
        delBtn.style.opacity = (checked.length === 0) ? '0.6' : '1';
    }
    var togBtn = document.getElementById('toggleSelectedBtn');
    if (togBtn) {
        togBtn.innerText = '⚡ Toggle Selected (' + checked.length + ')';
        togBtn.disabled = (checked.length === 0);
        togBtn.style.opacity = (checked.length === 0) ? '0.6' : '1';
    }
}

function submitBatchAction(actionName) {
    var checked = document.querySelectorAll('.loc-check:checked');
    if (checked.length === 0) {
        alert('Please select at least one item first.');
        return false;
    }
    var actionLabel = (actionName === 'delete_batch') ? 'permanently DELETE' : 'TOGGLE active status for';
    if (!confirm('Are you sure you want to ' + actionLabel + ' ' + checked.length + ' selected item(s)?')) {
        return false;
    }
    var ids = [];
    for (var i = 0; i < checked.length; i++) {
        ids.push(checked[i].value);
    }
    document.getElementById('batchActionInput').value = actionName;
    document.getElementById('batchTargetIds').value = ids.join(',');
    document.getElementById('batchActionForm').submit();
}

function openEditSourceModal(id, name, desc, uuid, active) {
    document.getElementById('modalTitle').innerText = 'Edit Sample Source #' + id;
    document.getElementById('modalAction').value = 'save_source';
    document.getElementById('modalId').value = id;
    document.getElementById('modalName').value = name;
    document.getElementById('modalDesc').value = desc;
    var uuidInp = document.getElementById('modalUuid');
    if (uuidInp) uuidInp.value = uuid;
    document.getElementById('modalActive').value = active ? 'true' : 'false';
    document.getElementById('locModalOverlay').style.display = 'flex';
}

function openEditLocationModal(id, name, desc, addr, phone, active) {
    document.getElementById('modalTitle').innerText = 'Edit Lab Location #' + id;
    document.getElementById('modalAction').value = 'save_location';
    document.getElementById('modalId').value = id;
    document.getElementById('modalName').value = name;
    document.getElementById('modalDesc').value = desc;
    var addrInp = document.getElementById('modalAddr');
    if (addrInp) addrInp.value = addr;
    var phoneInp = document.getElementById('modalPhone');
    if (phoneInp) phoneInp.value = phone;
    document.getElementById('modalActive').value = active ? 'true' : 'false';
    document.getElementById('locModalOverlay').style.display = 'flex';
}

function openAddModal() {
    var isSource = "<%= viewMode %>" === "source";
    document.getElementById('modalTitle').innerText = isSource ? 'Add New Sample Source' : 'Add New Lab Location';
    document.getElementById('modalAction').value = isSource ? 'save_source' : 'save_location';
    document.getElementById('modalId').value = '';
    document.getElementById('modalName').value = '';
    document.getElementById('modalDesc').value = '';
    var uuidInp = document.getElementById('modalUuid');
    if (uuidInp) uuidInp.value = '';
    var addrInp = document.getElementById('modalAddr');
    if (addrInp) addrInp.value = '';
    var phoneInp = document.getElementById('modalPhone');
    if (phoneInp) phoneInp.value = '';
    document.getElementById('modalActive').value = 'true';
    document.getElementById('locModalOverlay').style.display = 'flex';
}

function closeEditModal() {
    document.getElementById('locModalOverlay').style.display = 'none';
}
</script>
