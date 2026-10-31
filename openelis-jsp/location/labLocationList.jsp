<%@ page language="java" contentType="application/json; charset=utf-8"
    import="java.sql.*, java.util.*, java.io.*"%>
<%
    response.setContentType("application/json");
    response.setCharacterEncoding("UTF-8");
    response.setHeader("Access-Control-Allow-Origin", "*");
    response.setHeader("Access-Control-Allow-Methods", "GET");

    String dbUrl = "jdbc:postgresql://openelisdb:5432/clinlims";
    String dbUser = "clinlims";
    String dbPass = "clinlims";

    StringBuilder json = new StringBuilder();
    json.append("{\"locations\":[");

    try {
        Class.forName("org.postgresql.Driver");
        Connection conn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
        PreparedStatement ps = conn.prepareStatement(
            "SELECT id, name, description, address, phone FROM lab_location WHERE is_active = true ORDER BY name");
        ResultSet rs = ps.executeQuery();

        boolean first = true;
        while (rs.next()) {
            if (!first) json.append(",");
            first = false;
            json.append("{");
            json.append("\"id\":").append(rs.getInt("id"));
            json.append(",\"name\":\"").append(escapeJson(rs.getString("name"))).append("\"");
            json.append(",\"description\":\"").append(escapeJson(rs.getString("description"))).append("\"");
            json.append(",\"address\":\"").append(escapeJson(rs.getString("address"))).append("\"");
            json.append(",\"phone\":\"").append(escapeJson(rs.getString("phone"))).append("\"");
            json.append("}");
        }
        rs.close(); ps.close(); conn.close();
    } catch (Exception e) {
        json.append("{\"error\":\"").append(escapeJson(e.getMessage())).append("\"}");
    }

    json.append("]}");
    out.print(json.toString());
%>
<%!
    private String escapeJson(String s) {
        if (s == null) return "";
        return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t");
    }
%>
