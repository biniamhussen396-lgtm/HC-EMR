package us.mn.state.health.lims.test.action;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.util.ArrayList;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;
import org.apache.struts.action.DynaActionForm;
import org.bahmni.feed.openelis.externalreference.dao.ExternalReferenceDao;
import org.bahmni.feed.openelis.externalreference.daoimpl.ExternalReferenceDaoImpl;
import org.bahmni.feed.openelis.externalreference.valueholder.ExternalReference;
import us.mn.state.health.lims.common.action.BaseAction;
import us.mn.state.health.lims.common.action.IActionConstants;
import us.mn.state.health.lims.common.log.LogEvent;
import us.mn.state.health.lims.hibernate.HibernateUtil;
import us.mn.state.health.lims.typeofsample.util.TypeOfSampleUtil;
import et.edu.uog.AvailabilitySender;

public class TestSetActiveAction extends BaseAction {
    private boolean isNew = false;

    public TestSetActiveAction() {}

    protected ActionForward performAction(ActionMapping mapping, ActionForm form, HttpServletRequest request, HttpServletResponse response) throws Exception {
        String forward = "success";

        List<String> idList = new ArrayList<String>();
        if (form instanceof DynaActionForm) {
            try {
                String[] formIds = (String[]) ((DynaActionForm) form).get("selectedIDs");
                if (formIds != null) {
                    for (String id : formIds) {
                        if (id != null && !id.trim().isEmpty() && !idList.contains(id.trim())) {
                            idList.add(id.trim());
                        }
                    }
                }
            } catch (Exception ignored) {}
        }

        String[] paramIds = request.getParameterValues("selectedIDs");
        if (paramIds != null) {
            for (String id : paramIds) {
                if (id != null && !id.trim().isEmpty() && !idList.contains(id.trim())) {
                    idList.add(id.trim());
                }
            }
        }

        String idParam = request.getParameter("ID");
        if (idParam != null && !idParam.trim().isEmpty() && !idList.contains(idParam.trim())) {
            idList.add(idParam.trim());
        }

        if (!idList.isEmpty()) {
            String activityStatus = request.getParameter("ActivityStatus");
            if (activityStatus == null || activityStatus.trim().isEmpty()) {
                activityStatus = "Y";
            } else {
                activityStatus = activityStatus.trim().toUpperCase();
            }

            for (String testId : idList) {
                System.out.println("TestSetActiveAction -> testId: " + testId + " status: " + activityStatus);

                // 1. Sync to OpenMRS via AvailabilitySender
                try {
                    ExternalReferenceDao extDao = new ExternalReferenceDaoImpl();
                    ExternalReference extRef = extDao.getDataByItemId(testId, "Test");
                    if (extRef != null && extRef.getExternalId() != null) {
                        String stateName = "Y".equalsIgnoreCase(activityStatus) ? "active" : "inactive";
                        System.out.println(extRef.getExternalId() + " : external reference syncing " + stateName);
                        AvailabilitySender.send(extRef.getExternalId(), stateName);
                    }
                } catch (Exception ex) {
                    LogEvent.logError("TestSetActiveAction", "AvailabilitySender", ex.toString());
                }

                // 2. Direct JDBC update to Postgres clinlims.test
                try {
                    Class.forName("org.postgresql.Driver");
                    Connection conn = DriverManager.getConnection("jdbc:postgresql://openelisdb:5432/clinlims", "clinlims", "clinlims");
                    PreparedStatement ps = conn.prepareStatement("UPDATE test SET is_active = ?, lastupdated = NOW() WHERE id = ?");
                    ps.setString(1, activityStatus);
                    ps.setInt(2, Integer.parseInt(testId));
                    ps.executeUpdate();
                    ps.close();
                    conn.close();
                } catch (Exception dbEx) {
                    LogEvent.logError("TestSetActiveAction", "directJdbcUpdate", dbEx.toString());
                }
            }

            // 3. Clear Hibernate session & TypeOfSampleUtil in-memory cache so fresh data is visible immediately
            try {
                HibernateUtil.getSession().clear();
                TypeOfSampleUtil.clearTestCache();
            } catch (Exception ignored) {}
        }

        request.setAttribute(IActionConstants.TEST_SET_ACTIVE, "true");
        return mapping.findForward(forward);
    }

    protected String getPageTitleKey() {
        return this.isNew ? "test.add.title" : "test.edit.title";
    }

    protected String getPageSubtitleKey() {
        return this.isNew ? "test.add.title" : "test.edit.title";
    }
}
