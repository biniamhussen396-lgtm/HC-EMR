<%@ page language="java" contentType="application/json; charset=utf-8"
    import="java.sql.*, java.util.*, org.json.*"%>
<%
    response.setHeader("Cache-Control", "no-cache, no-store, must-revalidate");
    response.setHeader("Pragma", "no-cache");
    response.setDateHeader("Expires", 0);
    response.setHeader("Access-Control-Allow-Origin", "*");

    String dbUrl = "jdbc:postgresql://openelisdb:5432/clinlims";
    String dbUser = "clinlims";
    String dbPass = "clinlims";

    Connection conn = null;
    PreparedStatement ps = null;
    ResultSet rs = null;

    JSONObject map = new JSONObject();
    JSONArray list = new JSONArray();

    try {
        Class.forName("org.postgresql.Driver");
        conn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
        String sql = "SELECT name, description FROM test WHERE UPPER(TRIM(COALESCE(is_active, 'N'))) = 'N' " +
                     "UNION ALL " +
                     "SELECT name, description FROM panel WHERE UPPER(TRIM(COALESCE(is_active, 'N'))) = 'N'";
        ps = conn.prepareStatement(sql);
        rs = ps.executeQuery();
        while (rs.next()) {
            String name = rs.getString("name");
            String desc = rs.getString("description");
            if (name != null && !name.trim().isEmpty()) {
                map.put(name.trim().toLowerCase(), true);
                list.put(name.trim());
            }
            if (desc != null && !desc.trim().isEmpty()) {
                map.put(desc.trim().toLowerCase(), true);
            }
        }
    } catch (Exception e) {
        map.put("error", e.getMessage());
    } finally {
        if (rs != null) try { rs.close(); } catch (Exception e) {}
        if (ps != null) try { ps.close(); } catch (Exception e) {}
        if (conn != null) try { conn.close(); } catch (Exception e) {}
    }

    String format = request.getParameter("format");
    if ("list".equalsIgnoreCase(format)) {
        out.print(list.toString());
    } else {
        out.print(map.toString());
    }
%>
