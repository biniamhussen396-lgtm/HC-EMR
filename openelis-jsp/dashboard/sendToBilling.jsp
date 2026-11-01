<%@ page language="java" contentType="application/json; charset=utf-8" import="java.util.*,us.mn.state.health.lims.hibernate.HibernateUtil,org.hibernate.*,org.json.*,java.io.*"%><%
    response.setHeader("Cache-Control", "no-cache");
    String orderId = request.getParameter("orderId");
    String patientId = request.getParameter("patientId");
    if (orderId == null || orderId.trim().isEmpty()) {
        out.print("{\"success\":false,\"error\":\"orderId is required\"}");
        return;
    }
    orderId = orderId.trim();
    if (patientId == null) patientId = "";
    patientId = patientId.trim();

    Session hSession = null;
    Transaction tx = null;
    List<String> availableNames = new ArrayList<String>();
    List<String> availableUuids = new ArrayList<String>();
    List<String> stockOutNames = new ArrayList<String>();
    List<String> stockOutUuids = new ArrayList<String>();

    try {
        hSession = HibernateUtil.getSession();
        tx = hSession.beginTransaction();

        java.math.BigDecimal sid = new java.math.BigDecimal(orderId);

        // Mark sent_to_billing in stock_out_selection strictly by sample_id
        hSession.createSQLQuery("UPDATE stock_out_selection SET sent_to_billing = TRUE, updated_at = CURRENT_TIMESTAMP WHERE sample_id = :sid")
            .setParameter("sid", sid).executeUpdate();

        // Find available test names for this sample
        org.hibernate.Query qAvail = hSession.createSQLQuery("SELECT DISTINCT test_name, concept_uuid FROM stock_out_selection WHERE sample_id = :sid AND status = 'available'")
            .setParameter("sid", sid);
        List availList = qAvail.list();
        if (availList != null) {
            for (Object obj : availList) {
                if (obj instanceof Object[]) {
                    Object[] r = (Object[]) obj;
                    if (r[0] != null) availableNames.add(r[0].toString().trim());
                    if (r[1] != null && !r[1].toString().trim().isEmpty()) availableUuids.add(r[1].toString().trim());
                }
            }
        }

        // Find stock-out test names for this sample to void in OpenMRS
        org.hibernate.Query qSo = hSession.createSQLQuery("SELECT DISTINCT test_name, concept_uuid FROM stock_out_selection WHERE sample_id = :sid AND status = 'stockout'")
            .setParameter("sid", sid);
        List soList = qSo.list();
        if (soList != null) {
            for (Object obj : soList) {
                if (obj instanceof Object[]) {
                    Object[] r = (Object[]) obj;
                    if (r[0] != null) stockOutNames.add(r[0].toString().trim());
                    if (r[1] != null && !r[1].toString().trim().isEmpty()) stockOutUuids.add(r[1].toString().trim());
                }
            }
        }

        // Find sample UUID for Odoo external_id mapping
        String sampleUuid = "";
        try {
            List uList = hSession.createSQLQuery("SELECT uuid FROM sample WHERE id = :sid LIMIT 1")
                .setParameter("sid", sid).list();
            if (uList != null && !uList.isEmpty() && uList.get(0) != null) {
                sampleUuid = uList.get(0).toString().trim();
            }
        } catch (Exception ignore) {}

        // Fetch patientRef if empty
        if (patientId.isEmpty()) {
            try {
                List pRows = hSession.createSQLQuery(
                    "SELECT pi.identity_data FROM sample_human sh " +
                    "JOIN patient_identity pi ON sh.patient_id = pi.patient_id " +
                    "WHERE (sh.samp_id = :sid OR sh.id = :sid) AND pi.identity_data IS NOT NULL AND TRIM(pi.identity_data) != '' " +
                    "ORDER BY LENGTH(pi.identity_data) ASC LIMIT 1"
                ).setParameter("sid", sid).list();
                if (pRows != null && !pRows.isEmpty() && pRows.get(0) != null) {
                    patientId = pRows.get(0).toString().trim();
                }
            } catch (Exception ignore) {}
        }

        tx.commit();

        // 1. Trigger Odoo add.available.lab.tests
        if (!availableNames.isEmpty() && !patientId.isEmpty()) {
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
                pyCmd.append("        'patientId': '").append(patientId).append("',\n");
                pyCmd.append("        'orderUuid': '").append(sampleUuid).append("',\n");
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

        // 2. Void stock-out tests in OpenMRS via REST API
        if (!stockOutNames.isEmpty() && !patientId.isEmpty()) {
            try {
                StringBuilder pyVoid = new StringBuilder();
                pyVoid.append("import urllib2, base64, json\n");
                pyVoid.append("try:\n");
                pyVoid.append("    p_req = urllib2.Request('http://openmrs:8080/openmrs/ws/rest/v1/patient?q=").append(patientId).append("&v=default')\n");
                pyVoid.append("    p_req.add_header('Authorization', 'Basic ' + base64.b64encode('admin:Admin123'))\n");
                pyVoid.append("    p_res = urllib2.urlopen(p_req)\n");
                pyVoid.append("    p_data = json.loads(p_res.read())\n");
                pyVoid.append("    if p_data.get('results'):\n");
                pyVoid.append("        p_uuid = p_data['results'][0]['uuid']\n");
                pyVoid.append("        o_req = urllib2.Request('http://openmrs:8080/openmrs/ws/rest/v1/order?patient=' + p_uuid + '&v=full')\n");
                pyVoid.append("        o_req.add_header('Authorization', 'Basic ' + base64.b64encode('admin:Admin123'))\n");
                pyVoid.append("        o_res = urllib2.urlopen(o_req)\n");
                pyVoid.append("        orders_data = json.loads(o_res.read())\n");
                pyVoid.append("        opener = urllib2.build_opener(urllib2.HTTPHandler)\n");
                pyVoid.append("        so_list = [");
                for (int k = 0; k < stockOutNames.size(); k++) {
                    if (k > 0) pyVoid.append(",");
                    pyVoid.append("'").append(stockOutNames.get(k).replace("'", "\\'").toLowerCase()).append("'");
                }
                pyVoid.append("]\n");
                pyVoid.append("        for ord_item in orders_data.get('results', []):\n");
                pyVoid.append("            disp = (ord_item.get('concept', {}).get('display') or '').strip().lower()\n");
                pyVoid.append("            ouuid = ord_item.get('uuid')\n");
                pyVoid.append("            for s_name in so_list:\n");
                pyVoid.append("                if s_name in disp or disp in s_name or (s_name == 'rbs' and 'random blood sugar' in disp):\n");
                pyVoid.append("                    v_req = urllib2.Request('http://openmrs:8080/openmrs/ws/rest/v1/order/' + ouuid + '?reason=Reagent+Out+of+Stock')\n");
                pyVoid.append("                    v_req.get_method = lambda: 'DELETE'\n");
                pyVoid.append("                    v_req.add_header('Authorization', 'Basic ' + base64.b64encode('admin:Admin123'))\n");
                pyVoid.append("                    try:\n");
                pyVoid.append("                        opener.open(v_req)\n");
                pyVoid.append("                    except Exception:\n");
                pyVoid.append("                        pass\n");
                pyVoid.append("                    break\n");
                pyVoid.append("except Exception:\n");
                pyVoid.append("    pass\n");

                ProcessBuilder pbVoid = new ProcessBuilder("python", "-c", pyVoid.toString());
                pbVoid.redirectErrorStream(true);
                Process procVoid = pbVoid.start();
                procVoid.waitFor();
            } catch (Exception ignore) {}
        }

        out.print("{\"success\":true,\"orderId\":\"" + orderId + "\",\"patientId\":\"" + patientId + "\",\"availableCount\":" + availableNames.size() + ",\"stockOutCount\":" + stockOutNames.size() + "}");
    } catch (Exception e) {
        if (tx != null) try { tx.rollback(); } catch (Exception ex) {}
        out.print("{\"success\":false,\"error\":\"" + (e.getMessage() != null ? e.getMessage().replace("\"", "\\\"") : "error") + "\"}");
    }
%>
