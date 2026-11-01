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
        java.math.BigDecimal altSid = null;
        try {
            List shRows = hSession.createSQLQuery(
                "SELECT CASE WHEN samp_id = :sid THEN id ELSE samp_id END FROM sample_human WHERE samp_id = :sid OR id = :sid LIMIT 1"
            ).setParameter("sid", sid).list();
            if (shRows != null && !shRows.isEmpty() && shRows.get(0) != null) {
                altSid = new java.math.BigDecimal(shRows.get(0).toString().trim());
            }
        } catch (Exception ignore) {}

        org.hibernate.Query q = hSession.createSQLQuery(
            "SELECT DISTINCT ON (test_name) test_id, test_name, status, concept_uuid FROM stock_out_selection " +
            "WHERE (sample_id = :sid" + (altSid != null ? " OR sample_id = :altSid" : "") + ") " +
            "ORDER BY test_name, id DESC"
        ).setParameter("sid", sid);
        if (altSid != null) q.setParameter("altSid", altSid);
        List rows = q.list();

        JSONArray arr = new JSONArray();
        for (Object row : rows) {
            Object[] cols = (Object[]) row;
            JSONObject obj = new JSONObject();
            obj.put("testId", cols[0] != null ? cols[0].toString() : "");
            obj.put("testName", cols[1] != null ? cols[1].toString() : "");
            obj.put("status", cols[2] != null ? cols[2].toString() : "pending");
            obj.put("conceptUuid", cols.length > 3 && cols[3] != null ? cols[3].toString() : "");
            arr.put(obj);
        }
        out.print(arr.toString());
    } catch (Exception e) {
        out.print("[]");
    }
%>