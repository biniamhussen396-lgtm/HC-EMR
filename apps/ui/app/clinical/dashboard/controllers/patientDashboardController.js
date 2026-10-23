'use strict';

angular.module('bahmni.clinical')
    .controller('PatientDashboardController', ['$scope', '$rootScope', 'clinicalAppConfigService', 'clinicalDashboardConfig', 'printer',
        '$state', 'spinner', 'visitSummary', 'appService', '$stateParams', 'diseaseTemplateService', 'patientContext', '$location', '$filter', '$http', 'paymentStatusService',
        function ($scope, $rootScope, clinicalAppConfigService, clinicalDashboardConfig, printer,
                  $state, spinner, visitSummary, appService, $stateParams, diseaseTemplateService, patientContext, $location, $filter, $http, paymentStatusService) {
            $scope.patient = patientContext.patient;
            $scope.patient.paymentStatus = false;
            $scope.buttonShow = false;
            var payment_config = appService.getAppDescriptor().getConfigValue("paymentConfig") || {};
            $scope.consultationTabPriv = false;
            $scope.isSuperAdmin = false;
            $rootScope.currentUser.privileges.forEach(function (priv) {
                if (priv.name === "Patient Dashboard - Consultation tab") {
                    $scope.consultationTabPriv = true;
                }
                if (priv.name === "SuperAdmin") {
                    $scope.isSuperAdmin = true;
                }
            });
            $scope.activeVisit = $scope.visitHistory.activeVisit;
            $scope.activeVisitData = {};
            $scope.obsIgnoreList = clinicalAppConfigService.getObsIgnoreList();
            $scope.clinicalDashboardConfig = clinicalDashboardConfig;
            $scope.visitSummary = visitSummary;
            $scope.enrollment = $stateParams.enrollment;
            $scope.isDashboardPrinting = false;
            var programConfig = appService.getAppDescriptor().getConfigValue("program") || {};
            $state.discardChanges = false;

            $scope.paymentStatus = function () {
                if (!payment_config["disable checking"]) {
                    paymentStatusService.getPaymentStatus($scope.patient.identifier).then(function (response) {
                        var isPaid = response.data && response.data.status === "PAID";
                        $scope.buttonShow = isPaid;
                        $scope.patient.paymentStatus = isPaid;
                    }).catch(function () {
                        $scope.buttonShow = false;
                        $scope.patient.paymentStatus = false;
                    });
                } else {
                    .buttonShow = true;
                    .patient.paymentStatus = true;
                }
            };

            $scope.markAsPaid = function () {
                paymentStatusService.markAsPaid($scope.patient.identifier).then(function () {
                    $scope.buttonShow = true;
                    $scope.patient.paymentStatus = true;
                });
            };

            $scope.markAsUnpaid = function () {
                paymentStatusService.markAsUnpaid($scope.patient.identifier).then(function () {
                    $scope.buttonShow = false;
                    $scope.patient.paymentStatus = false;
                });
            };

            $scope.ipdDashboard = {
                hostData: {
                    patientId: $stateParams.patientUuid,
                    forDate: new Date().toUTCString()
                }
            };

            $scope.alergyData = {
                name: 'Customised for me!!!'
            };

            $scope.alergyApi = {
                callback: function () {
                    alert("We have a full fledged problem");
                }
            };

            $scope.stateChange = function () {
                return $state.current.name === 'patient.dashboard.show';
            };

            var cleanUpListenerSwitchDashboard = $scope.$on("event:switchDashboard", function (event, dashboard) {
                $scope.init(dashboard);
            });

            var cleanUpListenerPrintForm = $scope.$on("event:printForm", function(event, data){
                data.currentDashboardTemplateUrl = 'dashboard/views/formPrint.html';
                printer.print('dashboard/views/dashboardPrint.html', data);
            });

            var cleanUpListenerPrintDashboard = $scope.$on("event:printDashboard", function (event, tab) {
                var printScope = $scope.$new();
                printScope.isDashboardPrinting = true;
                printScope.tabBeingPrinted = tab || clinicalDashboardConfig.currentTab;
                var dashboardModel = Bahmni.Common.DisplayControl.Dashboard.create(printScope.tabBeingPrinted, $filter);
                spinner.forPromise(diseaseTemplateService.getLatestDiseaseTemplates(
                    $stateParams.patientUuid,
                    clinicalDashboardConfig.getDiseaseTemplateSections(printScope.tabBeingPrinted),
                    null,
                    null
                ).then(function (diseaseTemplate) {
                    printScope.diseaseTemplates = diseaseTemplate;
                    printScope.sectionGroups = dashboardModel.getSections(printScope.diseaseTemplates);
                    printer.printFromScope('dashboard/views/dashboardPrint.html', printScope);
                }));
            });

            $scope.$on("$destroy", function () {
                cleanUpListenerSwitchDashboard();
                cleanUpListenerPrintDashboard();
                cleanUpListenerPrintForm();
            });

            var addTabNameToParams = function (board) {
                $location.search('currentTab', board.translationKey);
            };

            var getCurrentTab = function () {
                var currentTabKey = $location.search().currentTab;
                var currentTab = $state.current.dashboard;
                if (currentTabKey) {
                    currentTab = _.find(clinicalDashboardConfig.visibleTabs, function (tab) {
                        return tab.translationKey === currentTabKey;
                    });
                }
                return (currentTab != undefined ? currentTab : clinicalDashboardConfig.currentTab);
            };

            $scope.init = function (dashboard) {
                dashboard.startDate = null;
                dashboard.endDate = null;
                if (programConfig.showDetailsWithinDateRange) {
                    dashboard.startDate = $stateParams.dateEnrolled;
                    dashboard.endDate = $stateParams.dateCompleted;
                }
                $state.current.dashboard = dashboard;
                clinicalDashboardConfig.switchTab(dashboard);
                addTabNameToParams(dashboard);
                var dashboardModel = Bahmni.Common.DisplayControl.Dashboard.create(dashboard, $filter);
                diseaseTemplateService.getLatestDiseaseTemplates(
                    $stateParams.patientUuid, clinicalDashboardConfig.getDiseaseTemplateSections(), dashboard.startDate, dashboard.endDate).then(function (diseaseTemplate) {
                        $scope.diseaseTemplates = diseaseTemplate;
                        $scope.sectionGroups = dashboardModel.getSections($scope.diseaseTemplates);
                    });
                $scope.currentDashboardTemplateUrl = $state.current.views['dashboard-content'] ?
                    $state.current.views['dashboard-content'].templateUrl : $state.current.views['dashboard-content'];
            };

            $scope.init(getCurrentTab());

            $scope.paymentStatus();
        }]);
