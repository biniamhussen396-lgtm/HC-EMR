package us.mn.state.health.lims.panel.action;

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
import us.mn.state.health.lims.common.log.LogEvent;
import us.mn.state.health.lims.common.util.SystemConfiguration;
import us.mn.state.health.lims.hibernate.HibernateUtil;
import us.mn.state.health.lims.typeofsample.util.TypeOfSampleUtil;
import et.edu.uog.AvailabilitySender;

public class PanelSetActiveAction extends BaseAction {
    public PanelSetActiveAction() {}

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

            for (String panelId : idList) {
                System.out.println("PanelSetActiveAction -> panelId: " + panelId + " status: " + activityStatus);

                try {
                    ExternalReferenceDao extDao = new ExternalReferenceDaoImpl();
                    ExternalReference extRef = extDao.getDataByItemId(panelId, "Panel");
                    if (extRef != null && extRef.getExternalId() != null) {
                        String stateName = "Y".equalsIgnoreCase(activityStatus) ? "active" : "inactive";
                        System.out.println(extRef.getExternalId() + " : external reference syncing " + stateName);
                        AvailabilitySender.send(extRef.getExternalId(), stateName);
                    }
                } catch (Exception ex) {
                    LogEvent.logError("PanelSetActiveAction", "AvailabilitySender", ex.toString());
                }

                try {
                    Class.forName("org.postgresql.Driver");
                    Connection conn = DriverManager.getConnection("jdbc:postgresql://openelisdb:5432/clinlims", "clinlims", "clinlims");
                    PreparedStatement ps = conn.prepareStatement("UPDATE panel SET is_active = ?, lastupdated = NOW() WHERE id = ?");
                    ps.setString(1, activityStatus);
                    ps.setInt(2, Integer.parseInt(panelId));
                    ps.executeUpdate();
                    ps.close();
                    conn.close();
                } catch (Exception dbEx) {
                    LogEvent.logError("PanelSetActiveAction", "directJdbcUpdate", dbEx.toString());
                }
            }

            try {
                HibernateUtil.getSession().clear();
                TypeOfSampleUtil.clearTestCache();
            } catch (Exception ignored) {}
        }

        request.setAttribute("setPanelActive", "true");
        return mapping.findForward(forward);
    }

    protected String getPageTitleKey() { return "panel.browse.title"; }
    protected String getPageSubtitleKey() { return "panel.browse.title"; }
    protected int getPageSize() { return SystemConfiguration.getInstance().getDefaultPageSize(); }
    protected String getDeactivateDisabled() { return "true"; }
}
