<%@ page language="java" contentType="application/json; charset=utf-8" import="java.util.*,us.mn.state.health.lims.hibernate.HibernateUtil,org.hibernate.*,org.json.*,java.io.*"%><%
    response.setHeader("Cache-Control", "no-cache");
    String sampleId = request.getParameter("sampleId");
    if (sampleId == null || sampleId.trim().isEmpty()) {
        out.print("[]");
        return;
    }
    Session hSession = null;
    try {
        hSession = HibernateUtil.getSession();
        java.math.BigDecimal sid = new java.math.BigDecimal(sampleId.trim());

        // 1. Query previously saved selections for this sample
        org.hibernate.Query q = hSession.createSQLQuery(
            "SELECT DISTINCT ON (test_name) test_id, test_name, status, concept_uuid FROM stock_out_selection " +
            "WHERE sample_id = :sid " +
            "ORDER BY test_name, id DESC"
        ).setParameter("sid", sid);
        List rows = q.list();

        // 2. If not yet evaluated, retrieve ordered tests directly from sample_item + analysis + test
        if (rows == null || rows.isEmpty()) {
            rows = hSession.createSQLQuery(
                "SELECT t.id AS test_id, t.name AS test_name, 'pending' AS status, COALESCE(er.external_id, '') AS concept_uuid " +
                "FROM sample_item si " +
                "JOIN analysis a ON si.id = a.sampitem_id " +
                "JOIN test t ON a.test_id = t.id " +
                "LEFT JOIN external_reference er ON (t.id = er.item_id AND er.type = 'Test') " +
                "WHERE si.samp_id = :sid " +
                "ORDER BY t.name ASC"
            ).setParameter("sid", sid).list();
        }

        JSONArray arr = new JSONArray();
        if (rows != null) {
            for (Object row : rows) {
                Object[] cols = (Object[]) row;
                JSONObject obj = new JSONObject();
                obj.put("testId", cols[0] != null ? cols[0].toString() : "");
                obj.put("testName", cols[1] != null ? cols[1].toString() : "");
                obj.put("status", cols[2] != null ? cols[2].toString() : "pending");
                obj.put("conceptUuid", cols.length > 3 && cols[3] != null ? cols[3].toString() : "");
                arr.put(obj);
            }
        }
        out.print(arr.toString());
    } catch (Exception e) {
        out.print("[]");
    }
%>
