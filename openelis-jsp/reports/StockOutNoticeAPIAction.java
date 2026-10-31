package org.openelisglobal.stockout;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.List;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;
import org.json.simple.JSONObject;
import org.json.simple.JSONArray;
import org.openelisglobal.common.action.BaseAction;
import org.openelisglobal.common.util.JSONUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

@Component
@Scope("prototype")
public class StockOutNoticeAPIAction extends BaseAction {

    @Autowired
    private StockOutNoticeService stockOutNoticeService;

    @Transactional
    public ActionForward execute(ActionMapping mapping, ActionForm form,
            HttpServletRequest request, HttpServletResponse response) throws Exception {

        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");

        PrintWriter out = response.getWriter();
        JSONObject json = new JSONObject();

        try {
            String action = request.getParameter("action");

            if ("generateNotice".equals(action)) {
                String accessionNumber = request.getParameter("accessionNumber");
                String[] voidedTestIds = request.getParameterValues("voidedTestIds[]");
                String voidReason = request.getParameter("voidReason");

                if (accessionNumber == null || voidedTestIds == null || voidReason == null) {
                    json.put("success", false);
                    json.put("message", "Missing required parameters");
                    out.print(json.toJSONString());
                    return null;
                }

                StockOutNoticeAction noticeAction = new StockOutNoticeAction();
                List<String> testIds = java.util.Arrays.asList(voidedTestIds);
                String result = noticeAction.generateNotice(accessionNumber, testIds, voidReason);

                if ("success".equals(result)) {
                    json.put("success", true);
                    json.put("noticeNumber", noticeAction.getNoticeNumber());
                    json.put("noticeDate", noticeAction.getNoticeDate());
                    json.put("patientName", noticeAction.getPatientName());
                    json.put("patientId", noticeAction.getPatientId());
                    json.put("accessionNumber", noticeAction.getAccessionNumber());

                    JSONArray testsArray = new JSONArray();
                    for (StockOutNoticeAction.VoidedTestVO test : noticeAction.getVoidedTests()) {
                        JSONObject testJson = new JSONObject();
                        testJson.put("testName", test.getTestName());
                        testJson.put("testCode", test.getTestCode());
                        testJson.put("sampleType", test.getSampleType());
                        testJson.put("voidReason", test.getVoidReason());
                        testJson.put("voidTime", test.getVoidTime());
                        testsArray.add(testJson);
                    }
                    json.put("voidedTests", testsArray);
                } else {
                    json.put("success", false);
                    json.put("message", "Failed to generate notice");
                }
            } else if ("getNotice".equals(action)) {
                String noticeNumber = request.getParameter("noticeNumber");
                // Retrieve existing notice logic here
                json.put("success", true);
                json.put("noticeNumber", noticeNumber);
            } else {
                json.put("success", false);
                json.put("message", "Invalid action");
            }

        } catch (Exception e) {
            json.put("success", false);
            json.put("message", e.getMessage());
            log.error("Error processing stock-out notice request", e);
        }

        out.print(json.toJSONString());
        out.flush();
        return null;
    }
}
