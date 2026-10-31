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
        List rows = hSession.createSQLQuery("SELECT test_id, test_name, status, concept_uuid FROM stock_out_selection WHERE sample_id = :sid ORDER BY id")
            .setParameter("sid", new java.math.BigDecimal(sampleId.trim())).list();
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