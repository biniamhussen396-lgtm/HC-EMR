package org.openelisglobal.stockout;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

import org.openelisglobal.common.action.BaseAction;
import org.openelisglobal.common.provider.ModelAutoCompleteProvider;
import org.openelisglobal.sample.service.SampleService;
import org.openelisglobal.sample.vo.SampleVO;
import org.openelisglobal.sampleitem.service.SampleItemService;
import org.openelisglobal.sampleitem.vo.SampleItemVO;
import org.openelisglobal.test.service.TestService;
import org.openelisglobal.test.vo.TestVO;
import org.openelisglobal.patient.service.PatientService;
import org.openelisglobal.patient.vo.Patient;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

@Component
@Scope("prototype")
public class StockOutNoticeAction extends BaseAction {

    @Autowired
    private SampleService sampleService;
    @Autowired
    private SampleItemService sampleItemService;
    @Autowired
    private TestService testService;
    @Autowired
    private PatientService patientService;

    private String noticeNumber;
    private String noticeDate;
    private String patientName;
    private String patientId;
    private String accessionNumber;
    private String receptionistName;
    private String orderingClinician;
    private List<VoidedTestVO> voidedTests;

    public StockOutNoticeAction() {
        voidedTests = new ArrayList<>();
    }

    @Transactional
    public String generateNotice(String accessionNumber, List<String> voidedTestIds, String voidReason) throws Exception {
        this.accessionNumber = accessionNumber;
        this.noticeNumber = "SO-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
        this.noticeDate = new java.text.SimpleDateFormat("dd/MM/yyyy HH:mm").format(new java.util.Date());

        SampleVO sample = sampleService.getSampleByAccessionNumber(accessionNumber);
        if (sample != null) {
            Patient patient = patientService.getPatientById(sample.getPatientId());
            if (patient != null) {
                this.patientName = patient.getFullName();
                this.patientId = patient.getPatientId();
            }
        }

        for (String testId : voidedTestIds) {
            TestVO test = testService.getTestById(testId);
            if (test != null) {
                VoidedTestVO voidedTest = new VoidedTestVO();
                voidedTest.setTestName(test.getTestName());
                voidedTest.setTestCode(test.getTestCode());
                voidedTest.setSampleType(test.getSampleType() != null ? test.getSampleType().getLocalizedTitle() : "");
                voidedTest.setVoidReason(voidReason);
                voidedTest.setVoidTime(new java.text.SimpleDateFormat("dd/MM/yyyy HH:mm").format(new java.util.Date()));
                voidedTests.add(voidedTest);
            }
        }

        return SUCCESS;
    }

    // Getters and Setters
    public String getNoticeNumber() { return noticeNumber; }
    public void setNoticeNumber(String noticeNumber) { this.noticeNumber = noticeNumber; }

    public String getNoticeDate() { return noticeDate; }
    public void setNoticeDate(String noticeDate) { this.noticeDate = noticeDate; }

    public String getPatientName() { return patientName; }
    public void setPatientName(String patientName) { this.patientName = patientName; }

    public String getPatientId() { return patientId; }
    public void setPatientId(String patientId) { this.patientId = patientId; }

    public String getAccessionNumber() { return accessionNumber; }
    public void setAccessionNumber(String accessionNumber) { this.accessionNumber = accessionNumber; }

    public String getReceptionistName() { return receptionistName; }
    public void setReceptionistName(String receptionistName) { this.receptionistName = receptionistName; }

    public String getOrderingClinician() { return orderingClinician; }
    public void setOrderingClinician(String orderingClinician) { this.orderingClinician = orderingClinician; }

    public List<VoidedTestVO> getVoidedTests() { return voidedTests; }
    public void setVoidedTests(List<VoidedTestVO> voidedTests) { this.voidedTests = voidedTests; }

    public static class VoidedTestVO {
        private String testName;
        private String testCode;
        private String sampleType;
        private String voidReason;
        private String voidTime;

        public String getTestName() { return testName; }
        public void setTestName(String testName) { this.testName = testName; }
        public String getTestCode() { return testCode; }
        public void setTestCode(String testCode) { this.testCode = testCode; }
        public String getSampleType() { return sampleType; }
        public void setSampleType(String sampleType) { this.sampleType = sampleType; }
        public String getVoidReason() { return voidReason; }
        public void setVoidReason(String voidReason) { this.voidReason = voidReason; }
        public String getVoidTime() { return voidTime; }
        public void setVoidTime(String voidTime) { this.voidTime = voidTime; }
    }
}
