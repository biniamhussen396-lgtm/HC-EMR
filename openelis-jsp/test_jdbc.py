import java.sql.Connection
import java.sql.DriverManager
import java.sql.PreparedStatement
import java.sql.ResultSet

try:
    Class.forName("org.postgresql.Driver")
    conn = DriverManager.getConnection("jdbc:postgresql://openelisdb:5432/clinlims", "clinlims", "clinlims")
    ps = conn.prepareStatement("SELECT sr.name FROM system_user_role sur JOIN system_role sr ON sur.role_id = sr.id WHERE sur.system_user_id = 1")
    rs = ps.executeQuery()
    while rs.next():
        print 'Role: ' + rs.getString(1)
    rs.close()
    ps.close()
    conn.close()
    print 'SUCCESS'
except Exception as e:
    print 'ERROR: ' + str(e)
