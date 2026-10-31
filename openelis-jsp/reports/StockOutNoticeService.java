package org.openelisglobal.stockout;

import java.util.List;

import org.openelisglobal.sample.service.SampleService;
import org.openelisglobal.sample.vo.SampleVO;
import org.openelisglobal.sampleitem.service.SampleItemService;
import org.openelisglobal.sampleitem.vo.SampleItemVO;
import org.openelisglobal.test.service.TestService;
import org.openelisglobal.test.vo.TestVO;
import org.openelisglobal.patient.service.PatientService;
import org.openelisglobal.patient.vo.Patient;
import org.openelisglobal.sample.service.SampleService.SampleType;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class StockOutNoticeService {

    @Autowired
    private SampleService sampleService;
    @Autowired
    private SampleItemService sampleItemService;
    @Autowired
    private TestService testService;
    @Autowired
    private PatientService patientService;

    @Transactional
    public StockOutNotice generateStockOutNotice(String accessionNumber, List<String> voidedTestIds, String voidReason) {
        StockOutNotice notice = new StockOutNotice();
        notice.setAccessionNumber(accessionNumber);
        notice.setNoticeNumber(generateNoticeNumber());
        notice.setNoticeDate(new java.text.SimpleDateFormat("dd/MM/yyyy HH:mm").format(new java.util.Date()));
        notice.setVoidReason(voidReason);

        // Get sample and patient info
        SampleVO sample = sampleService.getSampleByAccessionNumber(accessionNumber);
        if (sample != null) {
            Patient patient = patientService.getPatientById(sample.getPatientId());
            if (patient != null) {
                notice.setPatientName(patient.getFullName());
                notice.setPatientId(patient.getPatientId());
            }
        }

        // Get voided test details
        for (String testId : voidedTestIds) {
            TestVO test = testService.getTestById(testId);
            if (test != null) {
                StockOutNotice.VoidedTest voidedTest = new StockOutNotice.VoidedTest();
                voidedTest.setTestName(test.getTestName());
                voidedTest.setTestCode(test.getTestCode());
                voidedTest.setSampleType(test.getSampleType() != null ? test.getSampleType().getLocalizedTitle() : "");
                voidedTest.setVoidReason(voidReason);
                voidedTest.setVoidTime(new java.text.SimpleDateFormat("dd/MM/yyyy HH:mm").format(new java.util.Date()));
                notice.addVoidedTest(voidedTest);
            }
        }

        return notice;
    }

    private String generateNoticeNumber() {
        return "SO-" + System.currentTimeMillis() % 100000;
    }

    public static class StockOutNotice {
        private String noticeNumber;
        private String noticeDate;
        private String patientName;
        private String patientId;
        private String accessionNumber;
        private String voidReason;
        private java.util.List<VoidedTest> voidedTests = new java.util.ArrayList<>();

        public void addVoidedTest(VoidedTest test) {
            voidedTests.add(test);
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
        public String getVoidReason() { return voidReason; }
        public void setVoidReason(String voidReason) { this.voidReason = voidReason; }
        public java.util.List<VoidedTest> getVoidedTests() { return voidedTests; }
        public void setVoidedTests(java.util.List<VoidedTest> voidedTests) { this.voidedTests = voidedTests; }

        public static class VoidedTest {
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
}
