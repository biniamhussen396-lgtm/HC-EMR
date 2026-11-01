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

        // Mark sent_to_billing in stock_out_selection
        hSession.createSQLQuery("UPDATE stock_out_selection SET sent_to_billing = TRUE, updated_at = CURRENT_TIMESTAMP WHERE sample_id = :sid")
            .setParameter("sid", sid).executeUpdate();
        if (altSid != null && !altSid.equals(sid)) {
            hSession.createSQLQuery("UPDATE stock_out_selection SET sent_to_billing = TRUE, updated_at = CURRENT_TIMESTAMP WHERE sample_id = :altSid")
                .setParameter("altSid", altSid).executeUpdate();
        }

        // Find available test names for this sample
        org.hibernate.Query q = hSession.createSQLQuery("SELECT DISTINCT test_name, concept_uuid FROM stock_out_selection WHERE (sample_id = :sid" + (altSid != null ? " OR sample_id = :altSid" : "") + ") AND status = 'available'")
            .setParameter("sid", sid);
        if (altSid != null) q.setParameter("altSid", altSid);
        List rowList = q.list();
        if (rowList != null) {
            for (Object obj : rowList) {
                if (obj instanceof Object[]) {
                    Object[] r = (Object[]) obj;
                    if (r[0] != null) availableNames.add(r[0].toString().trim());
                    if (r[1] != null && !r[1].toString().trim().isEmpty()) availableUuids.add(r[1].toString().trim());
                }
            }
        }

        // Find sample UUID for Odoo external_id mapping
        String sampleUuid = "";
        try {
            List uList = hSession.createSQLQuery("SELECT uuid FROM sample WHERE id = :sid" + (altSid != null ? " OR id = :altSid" : "") + " LIMIT 1")
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

        // Trigger Odoo add.available.lab.tests
        if (!availableNames.isEmpty() && !patientId.isEmpty()) {
            try {
                StringBuilder pyCmd = new StringBuilder();
                pyCmd.append("import xmlrpclib\n");
                pyCmd.append("common = xmlrpclib.ServerProxy('http://odoo:8069/xmlrpc/2/common')\n");
                pyCmd.append("uid = common.authenticate('odoo', 'emrsync', 'Admin123', {})\n");
                pyCmd.append("if uid:\n");
                pyCmd.append("    models = xmlrpclib.ServerProxy('http://odoo:8069/xmlrpc/2/object')\n");
                pyCmd.append("    models.execute_kw('odoo', uid, 'Admin123', 'api.event.worker', 'process_event', [{\n");
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

        out.print("{\"success\":true,\"orderId\":\"" + orderId + "\",\"patientId\":\"" + patientId + "\",\"availableCount\":" + availableNames.size() + "}");
    } catch (Exception e) {
        if (tx != null) try { tx.rollback(); } catch (Exception ex) {}
        out.print("{\"success\":false,\"error\":\"" + (e.getMessage() != null ? e.getMessage().replace("\"", "\\\"") : "error") + "\"}");
    }
%>