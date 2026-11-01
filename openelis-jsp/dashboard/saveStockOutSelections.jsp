<%@ page language="java" contentType="application/json; charset=utf-8" import="java.util.*,us.mn.state.health.lims.hibernate.HibernateUtil,org.hibernate.*,org.json.*,java.io.*"%><%
    response.setHeader("Cache-Control", "no-cache");
    StringBuilder bodyBuilder = new StringBuilder();
    BufferedReader reader = request.getReader();
    String line;
    while ((line = reader.readLine()) != null) bodyBuilder.append(line);
    JSONObject json = new JSONObject(bodyBuilder.toString());

    String orderId = json.optString("orderId", "").trim();
    if (orderId.isEmpty()) {
        out.print("{\"success\":false,\"error\":\"orderId is required\"}");
        return;
    }
    JSONArray selections = json.optJSONArray("selections");

    Session hSession = null;
    Transaction tx = null;
    List<String> stockOutNames = new ArrayList<String>();
    List<String> stockOutUuids = new ArrayList<String>();
    List<String> availableNames = new ArrayList<String>();
    List<String> availableUuids = new ArrayList<String>();
    String patientRef = "";

    try {
        hSession = HibernateUtil.getSession();
        tx = hSession.beginTransaction();

        java.math.BigDecimal sid = new java.math.BigDecimal(orderId);
        java.math.BigDecimal altSid = null;
        try {
            List shRows = hSession.createSQLQuery(
                "SELECT CASE WHEN samp_id = :sid THEN id ELSE samp_id END FROM sample_human WHERE samp_id = :sid OR id = :sid LIMIT 1"
            ).setParameter("sid", sid).list();
            if (shRows != null && !shRows.isEmpty() && shRows.get(0) != null) {
                altSid = new java.math.BigDecimal(shRows.get(0).toString().trim());
            }
        } catch (Exception ignore) {}

        // Get patient identifier (ST number) for Odoo sync
        try {
            List pRows = hSession.createSQLQuery(
                "SELECT pi.identity_data FROM sample_human sh " +
                "JOIN patient_identity pi ON sh.patient_id = pi.patient_id " +
                "JOIN patient_identity_type pit ON pi.identity_type_id = pit.id " +
                "WHERE (sh.samp_id = :sid OR sh.id = :sid) AND pit.identity_type IN ('ST', 'NATIONAL', 'SUBJECT') " +
                "ORDER BY CASE WHEN pit.identity_type = 'ST' THEN 1 WHEN pit.identity_type = 'NATIONAL' THEN 2 ELSE 3 END " +
                "LIMIT 1"
            ).setParameter("sid", sid).list();
            if (pRows != null && !pRows.isEmpty() && pRows.get(0) != null) {
                patientRef = pRows.get(0).toString().trim();
            }
        } catch (Exception ignore) {}

        if (patientRef.isEmpty()) {
            try {
                List pRows = hSession.createSQLQuery(
                    "SELECT pi.identity_data FROM sample_human sh " +
                    "JOIN patient_identity pi ON sh.patient_id = pi.patient_id " +
                    "WHERE (sh.samp_id = :sid OR sh.id = :sid) AND pi.identity_data IS NOT NULL AND TRIM(pi.identity_data) != '' " +
                    "ORDER BY LENGTH(pi.identity_data) ASC LIMIT 1"
                ).setParameter("sid", sid).list();
                if (pRows != null && !pRows.isEmpty() && pRows.get(0) != null) {
                    patientRef = pRows.get(0).toString().trim();
                }
            } catch (Exception ignore) {}
        }

        hSession.createSQLQuery("DELETE FROM stock_out_selection WHERE sample_id = :sid")
            .setParameter("sid", sid).executeUpdate();
        if (altSid != null && !altSid.equals(sid)) {
            hSession.createSQLQuery("DELETE FROM stock_out_selection WHERE sample_id = :altSid")
                .setParameter("altSid", altSid).executeUpdate();
        }

        if (selections != null) {
            for (int i = 0; i < selections.length(); i++) {
                JSONObject s = selections.getJSONObject(i);
                int tid = s.optInt("testId", 0);
                String tn = s.optString("testName", "").trim();
                String st = s.optString("status", "pending").trim();
                String conceptUuid = s.optString("conceptUuid", "").trim();

                // If testId is missing, look up from test table
                if (tid == 0 && !tn.isEmpty()) {
                    try {
                        List tRows = hSession.createSQLQuery("SELECT id FROM test WHERE LOWER(name) = :tn OR LOWER(description) = :tn LIMIT 1")
                            .setParameter("tn", tn.toLowerCase()).list();
                        if (tRows != null && !tRows.isEmpty() && tRows.get(0) != null) {
                            tid = ((Number) tRows.get(0)).intValue();
                        }
                    } catch (Exception ignore) {}
                }

                // If conceptUuid is missing, look up from external_reference
                if (conceptUuid.isEmpty() && tid > 0) {
                    try {
                        List uRows = hSession.createSQLQuery("SELECT external_id FROM external_reference WHERE item_id = :tid AND type = 'Test' LIMIT 1")
                            .setParameter("tid", tid).list();
                        if (uRows != null && !uRows.isEmpty() && uRows.get(0) != null) {
                            conceptUuid = uRows.get(0).toString().trim();
                        }
                    } catch (Exception ignore) {}
                }

                if ("stockout".equalsIgnoreCase(st)) {
                    stockOutNames.add(tn);
                    if (!conceptUuid.isEmpty()) stockOutUuids.add(conceptUuid);
                } else if ("available".equalsIgnoreCase(st)) {
                    availableNames.add(tn);
                    if (!conceptUuid.isEmpty()) availableUuids.add(conceptUuid);
                }

                hSession.createSQLQuery("INSERT INTO stock_out_selection (sample_id, test_id, test_name, status, concept_uuid, created_at, updated_at) VALUES (:sid, :tid, :tn, :st, :cu, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)")
                    .setParameter("sid", sid)
                    .setParameter("tid", tid)
                    .setParameter("tn", tn)
                    .setParameter("st", st)
                    .setParameter("cu", conceptUuid)
                    .executeUpdate();
                if (altSid != null && !altSid.equals(sid)) {
                    hSession.createSQLQuery("INSERT INTO stock_out_selection (sample_id, test_id, test_name, status, concept_uuid, created_at, updated_at) VALUES (:sid, :tid, :tn, :st, :cu, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)")
                        .setParameter("sid", altSid)
                        .setParameter("tid", tid)
                        .setParameter("tn", tn)
                        .setParameter("st", st)
                        .setParameter("cu", conceptUuid)
                        .executeUpdate();
                }
            }
        }

        tx.commit();

        // 1. Protect billing in Odoo: cancel/unlink stock-out lines AND void in OpenMRS
        if (!stockOutNames.isEmpty() && !patientRef.isEmpty()) {
            try {
                StringBuilder pyCmd = new StringBuilder();
                pyCmd.append("import xmlrpclib, urllib2, base64, json\n");
                pyCmd.append("common = xmlrpclib.ServerProxy('http://odoo:8069/xmlrpc/2/common')\n");
                pyCmd.append("uid = common.authenticate('odoo', 'emrsync', 'Admin123', {})\n");
                pyCmd.append("pwd = 'Admin123'\n");
                pyCmd.append("if not uid:\n");
                pyCmd.append("    uid = common.authenticate('odoo', 'admin', 'admin', {})\n");
                pyCmd.append("    pwd = 'admin'\n");
                pyCmd.append("if uid:\n");
                pyCmd.append("    models = xmlrpclib.ServerProxy('http://odoo:8069/xmlrpc/2/object')\n");
                pyCmd.append("    models.execute_kw('odoo', uid, pwd, 'api.event.worker', 'process_event', [{\n");
                pyCmd.append("        'category': 'cancel.order',\n");
                pyCmd.append("        'patientId': '").append(patientRef).append("',\n");
                pyCmd.append("        'stockOutTestNames': [");
                for (int k = 0; k < stockOutNames.size(); k++) {
                    if (k > 0) pyCmd.append(",");
                    pyCmd.append("'").append(stockOutNames.get(k).replace("'", "\\'")).append("'");
                }
                pyCmd.append("],\n");
                pyCmd.append("        'stockOutTestUuids': [");
                for (int k = 0; k < stockOutUuids.size(); k++) {
                    if (k > 0) pyCmd.append(",");
                    pyCmd.append("'").append(stockOutUuids.get(k).replace("'", "\\'")).append("'");
                }
                pyCmd.append("]\n");
                pyCmd.append("    }])\n");

                // Void matching active orders in OpenMRS
                pyCmd.append("try:\n");
                pyCmd.append("    p_req = urllib2.Request('http://openmrs:8080/openmrs/ws/rest/v1/patient?q=").append(patientRef).append("&v=default')\n");
                pyCmd.append("    p_req.add_header('Authorization', 'Basic ' + base64.b64encode('admin:Admin123'))\n");
                pyCmd.append("    p_res = urllib2.urlopen(p_req)\n");
                pyCmd.append("    p_data = json.loads(p_res.read())\n");
                pyCmd.append("    if p_data.get('results'):\n");
                pyCmd.append("        p_uuid = p_data['results'][0]['uuid']\n");
                pyCmd.append("        o_req = urllib2.Request('http://openmrs:8080/openmrs/ws/rest/v1/order?patient=' + p_uuid + '&v=full')\n");
                pyCmd.append("        o_req.add_header('Authorization', 'Basic ' + base64.b64encode('admin:Admin123'))\n");
                pyCmd.append("        o_res = urllib2.urlopen(o_req)\n");
                pyCmd.append("        orders_data = json.loads(o_res.read())\n");
                pyCmd.append("        opener = urllib2.build_opener(urllib2.HTTPHandler)\n");
                pyCmd.append("        so_list = [");
                for (int k = 0; k < stockOutNames.size(); k++) {
                    if (k > 0) pyCmd.append(",");
                    pyCmd.append("'").append(stockOutNames.get(k).replace("'", "\\'").toLowerCase()).append("'");
                }
                pyCmd.append("]\n");
                pyCmd.append("        for ord_item in orders_data.get('results', []):\n");
                pyCmd.append("            disp = (ord_item.get('concept', {}).get('display') or '').strip().lower()\n");
                pyCmd.append("            ouuid = ord_item.get('uuid')\n");
                pyCmd.append("            for s_name in so_list:\n");
                pyCmd.append("                if s_name in disp or disp in s_name or (s_name == 'rbs' and 'random blood sugar' in disp):\n");
                pyCmd.append("                    v_req = urllib2.Request('http://openmrs:8080/openmrs/ws/rest/v1/order/' + ouuid + '?reason=Reagent+Out+of+Stock')\n");
                pyCmd.append("                    v_req.get_method = lambda: 'DELETE'\n");
                pyCmd.append("                    v_req.add_header('Authorization', 'Basic ' + base64.b64encode('admin:Admin123'))\n");
                pyCmd.append("                    try:\n");
                pyCmd.append("                        opener.open(v_req)\n");
                pyCmd.append("                    except Exception:\n");
                pyCmd.append("                        pass\n");
                pyCmd.append("                    break\n");
                pyCmd.append("except Exception:\n");
                pyCmd.append("    pass\n");

                ProcessBuilder pb = new ProcessBuilder("python", "-c", pyCmd.toString());
                pb.redirectErrorStream(true);
                Process proc = pb.start();
                proc.waitFor();
            } catch (Exception ignore) {}
        }

        // 2. Add evaluated and confirmed AVAILABLE tests to Odoo for billing
        if (!availableNames.isEmpty() && !patientRef.isEmpty()) {
            try {
                StringBuilder pyCmd = new StringBuilder();
                pyCmd.append("import xmlrpclib\n");
                pyCmd.append("common = xmlrpclib.ServerProxy('http://odoo:8069/xmlrpc/2/common')\n");
                pyCmd.append("uid = common.authenticate('odoo', 'emrsync', 'Admin123', {})\n");
                pyCmd.append("pwd = 'Admin123'\n");
                pyCmd.append("if not uid:\n");
                pyCmd.append("    uid = common.authenticate('odoo', 'admin', 'admin', {})\n");
                pyCmd.append("    pwd = 'admin'\n");
                pyCmd.append("if uid:\n");
                pyCmd.append("    models = xmlrpclib.ServerProxy('http://odoo:8069/xmlrpc/2/object')\n");
                pyCmd.append("    models.execute_kw('odoo', uid, pwd, 'api.event.worker', 'process_event', [{\n");
                pyCmd.append("        'category': 'add.available.lab.tests',\n");
                pyCmd.append("        'patientId': '").append(patientRef).append("',\n");
                pyCmd.append("        'availableTestNames': [");
                for (int k = 0; k < availableNames.size(); k++) {
                    if (k > 0) pyCmd.append(",");
                    pyCmd.append("'").append(availableNames.get(k).replace("'", "\\'")).append("'");
                }
                pyCmd.append("],\n");
                pyCmd.append("        'availableTestUuids': [");
                for (int k = 0; k < availableUuids.size(); k++) {
                    if (k > 0) pyCmd.append(",");
                    pyCmd.append("'").append(availableUuids.get(k).replace("'", "\\'")).append("'");
                }
                pyCmd.append("]\n");
                pyCmd.append("    }])\n");

                ProcessBuilder pb = new ProcessBuilder("python", "-c", pyCmd.toString());
                pb.redirectErrorStream(true);
                Process proc = pb.start();
                proc.waitFor();
            } catch (Exception ignore) {}
        }

        out.print("{\"success\":true,\"patientRef\":\"" + patientRef + "\",\"stockOutCount\":" + stockOutNames.size() + ",\"availableCount\":" + availableNames.size() + "}");
    } catch (Exception e) {
        if (tx != null) try { tx.rollback(); } catch (Exception ex) {}
        String msg = e.getMessage() != null ? e.getMessage().replace("\"", "\\\"").replace("\n", " ") : "unknown error";
        out.print("{\"success\":false,\"error\":\"" + msg + "\"}");
    }
%>