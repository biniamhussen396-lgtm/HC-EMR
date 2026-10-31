<%@ page language="java" contentType="text/html; charset=utf-8"
    import="java.sql.*, java.util.*"%>
<%@ taglib uri="/tags/struts-bean" prefix="bean" %>
<%@ taglib uri="/tags/struts-html" prefix="html" %>
<%@ taglib uri="/tags/struts-logic" prefix="logic" %>

<style>
    .ls-container { max-width: 500px; margin: 50px auto; padding: 30px; background: white; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); }
    .ls-container h2 { color: #486086; text-align: center; margin-top: 0; }
    .ls-container p { color: #666; text-align: center; margin-bottom: 20px; }
    .ls-form-row { margin-bottom: 15px; }
    .ls-form-row label { display: block; font-weight: bold; margin-bottom: 5px; color: #333; }
    .ls-form-row select { width: 100%; padding: 10px; font-size: 14px; border: 1px solid #ccc; border-radius: 4px; }
    .ls-btn { width: 100%; padding: 12px; background: #486086; color: white; border: none; border-radius: 4px; font-size: 16px; cursor: pointer; }
    .ls-btn:hover { background: #3a4f6f; }
    .ls-btn:disabled { background: #ccc; cursor: not-allowed; }
    .ls-msg { padding: 8px 12px; border-radius: 4px; margin-bottom: 15px; font-weight: bold; background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    .ls-skip { text-align: center; margin-top: 15px; }
    .ls-skip a { color: #486086; text-decoration: underline; font-size: 13px; }
</style>

<%
    String dbUrl = "jdbc:postgresql://openelisdb:5432/clinlims";
    String dbUser = "clinlims";
    String dbPass = "clinlims";

    String msgType = "";
    String msgText = "";

    // Handle location selection
    String selectAction = request.getParameter("selectAction") != null ? request.getParameter("selectAction") : "";
    if ("select".equals(selectAction)) {
        String locationId = request.getParameter("locationId") != null ? request.getParameter("locationId") : "";
        String locationName = request.getParameter("locationName") != null ? request.getParameter("locationName") : "";

        if (!locationId.isEmpty()) {
            session.setAttribute("selectedLabLocationId", locationId);
            session.setAttribute("selectedLabLocationName", locationName);
            // Redirect to main page
            response.sendRedirect("MasterListsPage.do");
            return;
        } else {
            msgType = "error";
            msgText = "Please select a laboratory location.";
        }
    }

    // Check if user is admin (can skip location selection)
    boolean isAdmin = false;
    String currentUserName = "";
    int currentUserId = 0;
    try {
        us.mn.state.health.lims.login.valueholder.UserSessionData usd =
            (us.mn.state.health.lims.login.valueholder.UserSessionData) session.getAttribute("userSessionData");
        if (usd != null) {
            currentUserId = usd.getSystemUserId();
            currentUserName = usd.getElisUserName();

            Class.forName("org.postgresql.Driver");
            Connection conn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
            PreparedStatement ps = conn.prepareStatement(
                "SELECT 1 FROM system_user_role sur JOIN system_role sr ON sur.role_id = sr.id " +
                "WHERE sur.system_user_id = ? AND sr.name IN ('Maintenance Admin', 'User Admin') AND sr.active = true LIMIT 1");
            ps.setInt(1, currentUserId);
            ResultSet rs = ps.executeQuery();
            if (rs.next()) isAdmin = true;
            rs.close(); ps.close(); conn.close();
        }
    } catch (Exception e) {
        // default to non-admin
    }

    // Fetch active locations
    List<String[]> locations = new ArrayList<String[]>();
    try {
        Class.forName("org.postgresql.Driver");
        Connection conn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
        PreparedStatement ps = conn.prepareStatement("SELECT id, name, description FROM lab_location WHERE is_active = true ORDER BY name");
        ResultSet rs = ps.executeQuery();
        while (rs.next()) {
            locations.add(new String[]{rs.getString("id"), rs.getString("name"), rs.getString("description")});
        }
        rs.close(); ps.close(); conn.close();
    } catch (Exception e) {
        msgText = "Error loading locations: " + e.getMessage();
    }

    // Get previously selected location
    String prevLocationId = (String) session.getAttribute("selectedLabLocationId");
    String prevLocationName = (String) session.getAttribute("selectedLabLocationName");
%>

<div class="ls-container">
    <h2>Select Laboratory Location</h2>
    <p>Welcome<%= currentUserName != null ? ", " + currentUserName : "" %>. Please select your laboratory location to continue.</p>

    <% if (!msgText.isEmpty()) { %>
    <div class="ls-msg"><%= msgText %></div>
    <% } %>

    <% if (locations.isEmpty()) { %>
    <div class="ls-msg">No active laboratory locations found. Please contact your administrator.</div>
    <% } else { %>
    <form method="post" action="LocationSelect.do">
        <input type="hidden" name="selectAction" value="select">

        <div class="ls-form-row">
            <label>Laboratory Location:</label>
            <select name="locationId" id="lsLocationSelect" required>
                <option value="">-- Select Location --</option>
                <%
                    for (String[] loc : locations) {
                        String selected = loc[0].equals(prevLocationId) ? "selected" : "";
                        String label = loc[1];
                        if (loc[2] != null && !loc[2].isEmpty()) {
                            label += " - " + loc[2];
                        }
                        out.println("<option value='" + loc[0] + "' data-name='" + loc[1] + "' " + selected + ">" + label + "</option>");
                    }
                %>
            </select>
            <input type="hidden" name="locationName" id="lsLocationName" value="<%= prevLocationName != null ? prevLocationName : "" %>">
        </div>

        <button type="submit" class="ls-btn" id="lsSubmitBtn">Continue</button>
    </form>
    <% } %>

    <% if (isAdmin) { %>
    <div class="ls-skip">
        <a href="MasterListsPage.do">Skip - Access All Locations (Admin)</a>
    </div>
    <% } %>
</div>

<script>
document.getElementById('lsLocationSelect').addEventListener('change', function() {
    var selected = this.options[this.selectedIndex];
    var name = selected.getAttribute('data-name') || '';
    document.getElementById('lsLocationName').value = name;
});
</script>
