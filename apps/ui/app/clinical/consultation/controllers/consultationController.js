'use strict';

angular.module('bahmni.clinical').controller('ConsultationController',
    ['$http', '$scope', '$rootScope', '$state', '$location', '$translate', 'clinicalAppConfigService', 'diagnosisService', 'urlHelper', 'contextChangeHandler',
        'spinner', 'encounterService', 'messagingService', 'sessionService', 'retrospectiveEntryService', 'patientContext', '$q',
        'patientVisitHistoryService', '$stateParams', '$window', 'visitHistory', 'clinicalDashboardConfig', 'appService',
        'ngDialog', '$filter', 'configurations', 'visitConfig', 'conditionsService', 'configurationService', 'auditLogService', 'confirmBox', 'paymentStatusService',
        'virtualConsultService', 'adhocTeleconsultationService',
        function ($http, $scope, $rootScope, $state, $location, $translate, clinicalAppConfigService, diagnosisService, urlHelper, contextChangeHandler,
            spinner, encounterService, messagingService, sessionService, retrospectiveEntryService, patientContext, $q,
            patientVisitHistoryService, $stateParams, $window, visitHistory, clinicalDashboardConfig, appService,
                  ngDialog, $filter, configurations, visitConfig, conditionsService, configurationService, auditLogService, confirmBox, paymentStatusService,
                  virtualConsultService, adhocTeleconsultationService) {
            var ERROR = 1;
            var DateUtil = Bahmni.Common.Util.DateUtil;
            var getPreviousActiveCondition = Bahmni.Common.Domain.Conditions.getPreviousActiveCondition;
            var payment_config = appService.getAppDescriptor().getConfigValue("paymentConfig")
            var EMR_eAPTS_endPoint = appService.getAppDescriptor().getConfigValue("EMR_eAPTS_endPoint");
            var enableDrugStockStatusCheck = appService.getAppDescriptor().getConfigValue("enableDrugStockStatusCheck")
            $scope.togglePrintList = false;
            $scope.patient = patientContext.patient;
            $scope.patient.paymentStatus = false;
            async function fetchPatientHistory() {
                $scope.hasActiveVisit = false;
                const { url, queryParams } = {
                    url: '/openmrs/ws/rest/v1/bahmnicore/sql',
                    queryParams: { q: 'emrapi.sqlSearch.currentPatientActiveVisits', identifier: $scope.patient.identifier }
                };

                try {
                    const response = await $http.get(url, { params: queryParams, headers: { 'Content-Type': 'application/json' }, withCredentials: true });
                    const result = response.data;
                    if (result[0].NumberOfActiveVisit > 0) {
                        $scope.hasActiveVisit = true;

                    }
                } catch (error) {
                    throw new Error(`HTTP request failed with status: ${error.status} ${error.statusText}`);
                }
            }
            fetchPatientHistory();

            $scope.showDashboardMenu = false;
            $scope.showMobileMenu = false;
            $scope.stateChange = function () {
                return $state.current.name === 'patient.dashboard.show';
            };
            $scope.showComment = true;
            $scope.showSaveAndContinueButton = true;

            $scope.visitHistory = visitHistory;
            $scope.consultationBoardLink = clinicalAppConfigService.getConsultationBoardLink();
            $scope.showControlPanel = false;
            $scope.clinicalDashboardConfig = clinicalDashboardConfig;
            $scope.lastvisited = null;

            $scope.openConsultationInNewTab = function () {
                $window.open('#' + $scope.consultationBoardLink, '_blank');
            };

            $scope.toggleMobileMenu = function () {
                $scope.showMobileMenu = !$scope.showMobileMenu;
            };

            $scope.toggleDashboardMenu = function () {
                $scope.showDashboardMenu = !$scope.showDashboardMenu;
            };

            $scope.showDashboard = function (dashboard) {
                if (!clinicalDashboardConfig.isCurrentTab(dashboard)) {
                    $scope.$parent.$broadcast("event:switchDashboard", dashboard);
                }
                $scope.showDashboardMenu = false;
            };

            var setPrintAction = function (event, tab) {
                tab.print = function () {
                    $rootScope.$broadcast(event, tab);
                };
            };
            var setDashboardPrintAction = _.partial(setPrintAction, "event:printDashboard", _);
            var setVisitTabPrintAction = function (tab) {
                tab.print = function () {
                    var url = $state.href('patient.dashboard.visitPrint', {
                        visitUuid: visitHistory.activeVisit.uuid,
                        tab: tab.title,
                        print: 'print'
                    });
                    window.open(url, '_blank');
                };
            };

            clinicalDashboardConfig.allowAdhocTeleConsultation = appService.getAppDescriptor().getConfigValue('allowAdhocTeleConsultation');

            $scope.startAdhocTeleconsultationLink = function () {
                adhocTeleconsultationService.generateAdhocTeleconsultationLink(
                    {
                        patientUuid: $scope.patient.uuid,
                        provider: $rootScope.currentUser.username
                    }).then(function (data) {
                        if (!(data && data.data)) {
                            messagingService.showMessage('error', "{{'TELECON_ERROR_KEY' | translate }}");
                        }
                        virtualConsultService.launchMeeting(data.data.uuid, data.data.link);
                        if (data.data.notificationResults && data.data.notificationResults.length > 0) {
                            var message = data.data.notificationResults[0].message;
                            var status = data.data.notificationResults[0].status;
                            if (status === ERROR) {
                                messagingService.showMessage('error', message);
                            } else {
                                messagingService.showMessage('info', message);
                            }
                        }
                    });
            };

            _.each(visitConfig.tabs, setVisitTabPrintAction);
            _.each(clinicalDashboardConfig.tabs, setDashboardPrintAction);
            $scope.printList = _.concat(clinicalDashboardConfig.tabs, visitConfig.tabs);

            clinicalDashboardConfig.quickPrints = appService.getAppDescriptor().getConfigValue('quickPrints');
            $scope.printDashboard = function (tab) {
                if (tab) {
                    tab.print();
                } else {
                    clinicalDashboardConfig.currentTab.print();
                }
            };

            var getOrderUuid = function () {
                var params = {
                    q: "bahmni.sqlGet.orderUuid",
                    id: $scope.patient.identifier
                };
                return $http.get('/openmrs/ws/rest/v1/bahmnicore/sql', {
                    method: "GET",
                    params: params,
                    withCredentials: true
                });
            };

            $scope.buttonShow = false;

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
                    $scope.buttonShow = true;
                }
            }

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

            // async function paymentStatusFromObs() {
            //     const { url, queryParams } = {
            //         url: '/openmrs/ws/rest/v1/bahmnicore/sql',
            //         queryParams: { q: 'emrapi.paymentAllowance', person_uuid: patientContext.patient.uuid }
            //     };
            //     var currentDate = new Date();        
            //     try {
            //         const response = await $http.get(url, { params: queryParams, headers: { 'Content-Type': 'application/json' }, withCredentials: true });
            //         const result = response.data;
                    
            //         if (result && result.length > 0) {
            //             var dateStarted = new Date(result[0].date_created); // Ensure it's a Date object
            //             var dateDifferenceInDays = (currentDate - dateStarted) / (1000 * 60 * 60 * 24); // Convert to days

            //             if (dateDifferenceInDays <= 30) {
            //                 $scope.paymentAllowance = true;
            //             }        
            //         }
            //     } catch (error) {
            //         throw new Error(`HTTP request failed with status: ${error.status} ${error.statusText}`);
            //     }
            // }
            // paymentStatusFromObs();

            $scope.paymentStatus();

            $scope.isSuperAdmin = false;
            $rootScope.currentUser.privileges.forEach(function (priv) {
                if (priv.name === "SuperAdmin") {
                    $scope.isSuperAdmin = true;
                }
            });

            $scope.allowConsultation = function () {
                return appService.getAppDescriptor().getConfigValue('allowConsultationWhenNoOpenVisit');
            };

            $scope.closeDashboard = function (dashboard) {
                clinicalDashboardConfig.closeTab(dashboard);
                $scope.$parent.$parent.$broadcast("event:switchDashboard", clinicalDashboardConfig.currentTab);
            };

            $scope.closeAllDialogs = function () {
                ngDialog.closeAll();
            };

            $scope.availableBoards = [];
            $scope.configName = $stateParams.configName;

            $scope.getTitle = function (board) {
                return $filter('titleTranslate')(board);
            };

            $scope.showBoard = function (boardIndex) {
                $rootScope.collapseControlPanel();
                return buttonClickAction($scope.availableBoards[boardIndex]);
            };

            $scope.gotoPatientDashboard = function () {
                if (!isFormValid()) {
                    $scope.$parent.$parent.$broadcast("event:errorsOnForm");
                    return $q.when({});
                }
                if (contextChangeHandler.execute()["allow"]) {
                    var params = {
                        configName: $scope.configName,
                        patientUuid: patientContext.patient.uuid,
                        encounterUuid: undefined
                    };
                    if ($scope.dashboardDirty) {
                        params['dashboardCachebuster'] = Math.random();
                    }
                    $state.go("patient.dashboard.show", params);
                }
            };

            var isLongerName = function (value) {
                return value ? value.length > 18 : false;
            };

            $scope.getShorterName = function (value) {
                return isLongerName(value) ? value.substring(0, 15) + "..." : value;
            };

            $scope.isInEditEncounterMode = function () {
                return $stateParams.encounterUuid !== undefined && $stateParams.encounterUuid !== 'active';
            };

            $scope.enablePatientSearch = function () {
                return appService.getAppDescriptor().getConfigValue('allowPatientSwitchOnConsultation') === true;
            };

            var getInstitutionId = async function (visitTypeUuid) {
                var params = new URLSearchParams({
                    q: "emrapi.getDispensingUnitLocationUuid",
                    visitTypeUuid: visitTypeUuid,
                });

                try {
                    const response = await fetch('/openmrs/ws/rest/v1/bahmnicore/sql?' + params, {
                        method: "GET",
                        credentials: "include" // Similar to withCredentials: true in $http
                    });
                    if (!response.ok) {
                        throw new Error('Network response was not ok ' + response.statusText);
                    }
                    const data = await response.json();
                    return data[0].entity2_uuid;
                } catch (error) {
                    console.error('Error fetching institution ID:', error);
                    throw error;
                }
            };

            var setCurrentBoardBasedOnPath = function () {
                var currentPath = $location.url();
                var dashboardIndex = currentPath.indexOf('/dashboard');
                var dashboardPath = currentPath.substring(dashboardIndex);
                var board = _.find($scope.availableBoards, function (board) {
                    // if dashboardPath === "/dashboard/treatment?tabConfigName=allMedicationTabConfig"
                    if (board.url === "treatment") {
                        let visitTypeUuid;
                        if ($scope.visitHistory.activeVisit !== undefined) {
                            visitTypeUuid = $scope.visitHistory.activeVisit.visitType.uuid;
                        } else {
                            visitTypeUuid = $scope.visitHistory.visits[0].visitType.uuid;
                        }
                        if (enableDrugStockStatusCheck) {
                            getInstitutionId(visitTypeUuid).then(function (institutionId) {
                                const requestUrl = `${EMR_eAPTS_endPoint}?institutionId=${institutionId}`;

                                fetchStockStatusWithPopup(requestUrl);
                            }).catch(function (error) {
                                console.error('Error fetching institution ID:', error);
                            });
                        }

                        return _.includes(currentPath, board.extensionParams ? board.extensionParams.tabConfigName : board.url);
                    }
                    return _.includes(currentPath, board.url);
                });

                if (board) {
                    _.map($scope.availableBoards, function (availableBoard) {
                        availableBoard.isSelectedTab = false;
                    });
                    $scope.currentBoard = board;
                    $scope.currentBoard.isSelectedTab = true;
                }
            };

            // Function to fetch stock status and show SSL warning popup if fetch fails
            function fetchStockStatusWithPopup(requestUrl) {
                fetch(requestUrl)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`Network response was not ok: ${response.statusText}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        localStorage.setItem('stockStatus', JSON.stringify(data));
                    })
                    .catch(error => {
                        console.error('Error fetching stock status:', error);
                        // Show the popup when there is SSL warning error
                        loadPopupHtml('../clinical/consultation/views/sslWarningPopup.html').then(() => {
                            document.getElementById("proceedButton").addEventListener("click", function () {
                                window.open(requestUrl, '_blank'); // Open in a new tab
                                closePopup(); // Close popup after clicking "Proceed"
                            });
                        });
                    });
            }

            // Function to load HTML from external file and show it
            function loadPopupHtml(url) {
                return fetch(url)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Failed to load popup HTML');
                        }
                        return response.text();
                    })
                    .then(html => {
                        // Append the popup HTML to the body
                        document.body.insertAdjacentHTML('beforeend', html);
                    })
                    .catch(error => {
                        console.error('Error loading popup HTML:', error);
                    });
            }

            // Function to close the popup after the user proceeds
            function closePopup() {
                var popup = document.getElementById('sslWarningPopup');
                if (popup) {
                    popup.remove();
                }
            }



            var initialize = function () {
                var appExtensions = clinicalAppConfigService.getAllConsultationBoards();
                $scope.adtNavigationConfig = {forwardUrl: Bahmni.Clinical.Constants.adtForwardUrl, title: $translate.instant("CLINICAL_GO_TO_DASHBOARD_LABEL"), privilege: Bahmni.Clinical.Constants.adtPrivilege };
                $scope.availableBoards = $scope.availableBoards.concat(appExtensions);
                $scope.showSaveConfirmDialogConfig = appService.getAppDescriptor().getConfigValue('showSaveConfirmDialog');
                var adtNavigationConfig = appService.getAppDescriptor().getConfigValue('adtNavigationConfig');
                Object.assign($scope.adtNavigationConfig, adtNavigationConfig);
                setCurrentBoardBasedOnPath();

                // Clear localStorage after the page is reloaded
                window.addEventListener('beforeunload', () => {
                    localStorage.removeItem('stockStatus');
                });
            };

            $scope.shouldDisplaySaveConfirmDialogForStateChange = function (toState, toParams, fromState, fromParams) {
                if (toState.name.match(/patient.dashboard.show.*/)) {
                    return fromParams.patientUuid != toParams.patientUuid;
                }
                return true;
            };

            var cleanUpListenerStateChangeStart = $scope.$on('$stateChangeStart', function (event, toState, toParams, fromState, fromParams) {
                if ($scope.showSaveConfirmDialogConfig) {
                    if ($rootScope.hasVisitedConsultation && $scope.shouldDisplaySaveConfirmDialogForStateChange(toState, toParams, fromState, fromParams)) {
                        if ($scope.showConfirmationPopUp) {
                            event.preventDefault();
                            spinner.hide(toState.spinnerToken);
                            ngDialog.close();
                            $scope.toStateConfig = {toState: toState, toParams: toParams};
                            $scope.displayConfirmationDialog();
                        }
                    }
                }
                setCurrentBoardBasedOnPath();
            });

            $scope.adtNavigationURL = function (visitUuid) {
                return appService.getAppDescriptor().formatUrl($scope.adtNavigationConfig.forwardUrl, {'patientUuid': $scope.patient.uuid, 'visitUuid': visitUuid});
            };

            var cleanUpListenerErrorsOnForm = $scope.$on("event:errorsOnForm", function () {
                $scope.showConfirmationPopUp = true;
            });

            $scope.displayConfirmationDialog = function (event) {
                if ($rootScope.hasVisitedConsultation && $scope.showSaveConfirmDialogConfig) {
                    if (event) {
                        event.preventDefault();
                        $scope.targetUrl = event.currentTarget.getAttribute('href');
                    }
                    ngDialog.openConfirm({template: '../common/ui-helper/views/saveConfirmation.html', scope: $scope});
                }
                if ($scope.showTeleConsultationWindow) {
                    var childScope = {};
                    childScope.message = 'Please end teleconsultation before moving out of this window';
                    childScope.ok = okEvent;
                    if (event) {
                        event.preventDefault();
                        confirmBox({
                            scope: childScope,
                            actions: [{name: 'ok', display: 'Ok'}],
                            className: "ngdialog-theme-default delete-program-popup"
                        });
                    }
                }
            };

            var okEvent = function (closeDialog) {
                closeDialog();
            };

            var cleanUpListenerStateChangeSuccess = $scope.$on('$stateChangeSuccess', function (event, toState, toParams, fromState) {
                if (toState.name.match(/patient.dashboard.show.+/)) {
                    $rootScope.hasVisitedConsultation = true;
                    $scope.showConfirmationPopUp = true;
                    if ($scope.showSaveConfirmDialogConfig) {
                        $rootScope.$broadcast("event:pageUnload");
                    }
                }
                if ((toState.name === fromState.name) && (fromState.name === "patient.dashboard.show")) {
                    $rootScope.hasVisitedConsultation = false;
                }
            });

            $scope.$on("$destroy", function () {
                cleanUpListenerStateChangeSuccess();
                cleanUpListenerErrorsOnForm();
                cleanUpListenerStateChangeStart();
            });

            $scope.cancelTransition = function () {
                $scope.showConfirmationPopUp = true;
                ngDialog.close();
                delete $scope.targetUrl;
            };

            $scope.saveAndContinue = function () {
                $scope.showConfirmationPopUp = false;
                $scope.save($scope.toStateConfig);
                $window.onbeforeunload = null;
                ngDialog.close();
            };

            $scope.continueWithoutSaving = function () {
                $scope.showConfirmationPopUp = false;
                if ($scope.targetUrl) {
                    $window.open($scope.targetUrl, "_self");
                }
                $window.onbeforeunload = null;
                $state.go($scope.toStateConfig.toState, $scope.toStateConfig.toParams);
                ngDialog.close();
            };

            var getUrl = function (board) {
                var urlPrefix = urlHelper.getPatientUrl();
                var url = "/" + $stateParams.configName + (board.url ? urlPrefix + "/" + board.url : urlPrefix);
                var queryParams = [];
                if ($state.params.encounterUuid) {
                    queryParams.push("encounterUuid=" + $state.params.encounterUuid);
                }
                if ($state.params.programUuid) {
                    queryParams.push("programUuid=" + $state.params.programUuid);
                }

                if ($state.params.enrollment) {
                    queryParams.push("enrollment=" + $state.params.enrollment);
                }

                if ($state.params.dateEnrolled) {
                    queryParams.push("dateEnrolled=" + $state.params.dateEnrolled);
                }

                if ($state.params.dateCompleted) {
                    queryParams.push("dateCompleted=" + $state.params.dateCompleted);
                }

                var extensionParams = board.extensionParams;
                angular.forEach(extensionParams, function (extensionParamValue, extensionParamKey) {
                    queryParams.push(extensionParamKey + "=" + extensionParamValue);
                });

                if (!_.isEmpty(queryParams)) {
                    url = url + "?" + queryParams.join("&");
                }

                $scope.lastConsultationTabUrl.url = url;
                return $location.url(url);
            };

            $scope.openConsultation = function () {
                if ($scope.showSaveConfirmDialogConfig) {
                    $rootScope.$broadcast("event:pageUnload");
                }
                $scope.closeAllDialogs();
                $scope.collapseControlPanel();
                $rootScope.hasVisitedConsultation = true;
                switchToConsultationTab();
            };

            var switchToConsultationTab = function () {
                if ($scope.lastConsultationTabUrl.url) {
                    $location.url($scope.lastConsultationTabUrl.url);
                } else {
                    // Default tab
                    getUrl($scope.availableBoards[0]);
                }
            };

            var contextChange = function () {
                return contextChangeHandler.execute();
            };

            var buttonClickAction = function (board) {
                if ($scope.currentBoard === board) {
                    return;
                }
                if (!isFormValid()) {
                    $scope.$parent.$broadcast("event:errorsOnForm");
                    return;
                }

                contextChangeHandler.reset();
                _.map($scope.availableBoards, function (availableBoard) {
                    availableBoard.isSelectedTab = false;
                });

                $scope.currentBoard = board;
                $scope.currentBoard.isSelectedTab = true;
                return getUrl(board);
            };

            var preSaveEvents = function () {
                var observationForms = $scope.consultation.observationForms;
                var addedObservationForms = _.filter(observationForms, function (form) {
                    return form.isAdded;
                });
                _.each(addedObservationForms, function (form) {
                    if (form.component && form.events && form.events.onFormSave) {
                        try {
                            form.component.state.data = runEventScript(form.component.state.data,
                                form.events.onFormSave, form.component.props && form.component.props.patient);
                        } catch (error) {
                            throw error;
                        }
                    }
                });
            };

            var preSavePromise = function () {
                var deferred = $q.defer();
                var observationFilter = new Bahmni.Common.Domain.ObservationFilter();
                $scope.consultation.preSaveHandler.fire();
                $scope.lastvisited = $scope.consultation.lastvisited;
                var selectedObsTemplate = $scope.consultation.selectedObsTemplate;
                var tempConsultation = angular.copy($scope.consultation);
                tempConsultation.observations = observationFilter.filter(tempConsultation.observations);
                tempConsultation.consultationNote = observationFilter.filter([tempConsultation.consultationNote])[0];
                tempConsultation.labOrderNote = observationFilter.filter([tempConsultation.labOrderNote])[0];

                addFormObservations(tempConsultation);
                storeTemplatePreference(selectedObsTemplate);
                var visitTypeForRetrospectiveEntries = clinicalAppConfigService.getVisitTypeForRetrospectiveEntries();
                var defaultVisitType = clinicalAppConfigService.getDefaultVisitType();
                var encounterData = new Bahmni.Clinical.EncounterTransactionMapper().map(tempConsultation, $scope.patient, sessionService.getLoginLocationUuid(), retrospectiveEntryService.getRetrospectiveEntry(),
                    visitTypeForRetrospectiveEntries, defaultVisitType, $scope.isInEditEncounterMode(), $state.params.enrollment);
                deferred.resolve(encounterData);
                return deferred.promise;
            };

            $rootScope.currentUser.privileges.forEach(priv => {
                if (priv.name === "Patient Dashboard - Consultation tab")
                    $scope.consultationTabPriv = true;
            });

            var saveConditions = function () {
                return conditionsService.save($scope.consultation.conditions, $scope.patient.uuid)
                    .then(function () {
                        return conditionsService.getConditions($scope.patient.uuid);
                    }).then(function (savedConditions) {
                        return savedConditions;
                    });
            };

            var storeTemplatePreference = function (selectedObsTemplate) {
                var templates = [];
                _.each(selectedObsTemplate, function (template) {
                    var templateName = template.formName || template.conceptName;
                    var isTemplateAlreadyPresent = _.find(templates, function (template) {
                        return template === templateName;
                    });
                    if (_.isUndefined(isTemplateAlreadyPresent)) {
                        templates.push(templateName);
                    }
                });

                var data = {
                    "patientUuid": $scope.patient.uuid,
                    "providerUuid": $rootScope.currentProvider.uuid,
                    "templates": templates
                };

                if (!_.isEmpty(templates)) {
                    localStorage.setItem("templatePreference", JSON.stringify(data));
                }
            };

            var discontinuedDrugOrderValidation = function (removableDrugs) {
                var discontinuedDrugOrderValidationMessage;
                _.find(removableDrugs, function (drugOrder) {
                    if (!drugOrder.dateStopped) {
                        if (drugOrder._effectiveStartDate < moment()) {
                            discontinuedDrugOrderValidationMessage = "Please make sure that " + drugOrder.concept.name + " has a stop date between " + DateUtil.getDateWithoutTime(drugOrder._effectiveStartDate) + " and " + DateUtil.getDateWithoutTime(DateUtil.now());
                            return true;
                        } else {
                            discontinuedDrugOrderValidationMessage = drugOrder.concept.name + " should have stop date as today's date since it is a future drug order";
                            return true;
                        }
                    }
                });
                return discontinuedDrugOrderValidationMessage;
            };

            var addFormObservations = function (tempConsultation) {
                if (tempConsultation.observationForms) {
                    _.remove(tempConsultation.observations, function (observation) {
                        return observation.formNamespace;
                    });
                    _.each($scope.consultation.observationForms, function (observationForm) {
                        if (observationForm.component && observationForm.isAdded) {
                            var formObservations = observationForm.component.getValue();
                            _.each(formObservations.observations, function (obs) {
                                tempConsultation.observations.push(obs);
                            });
                        }
                    });
                }
            };

            var isObservationFormValid = function () {
                var valid = true;
                _.each($scope.consultation.observationForms, function (observationForm) {
                    if (valid && observationForm.component) {
                        var value = observationForm.component.getValue();
                        if (value.errors) {
                            messagingService.showMessage('error', "{{'CLINICAL_FORM_ERRORS_MESSAGE_KEY' | translate }}");
                            valid = false;
                        }
                    }
                });
                return valid;
            };

            var isFormValid = function () {
                var contxChange = contextChange();
                var shouldAllow = contxChange["allow"];
                var discontinuedDrugOrderValidationMessage = discontinuedDrugOrderValidation($scope.consultation.discontinuedDrugs);
                if (!shouldAllow) {
                    var errorMessage = contxChange["errorMessage"] ? contxChange["errorMessage"] : "{{'CLINICAL_FORM_ERRORS_MESSAGE_KEY' | translate }}";
                    messagingService.showMessage('error', errorMessage);
                } else if (discontinuedDrugOrderValidationMessage) {
                    var errorMessage = discontinuedDrugOrderValidationMessage;
                    messagingService.showMessage('error', errorMessage);
                }
                return shouldAllow && !discontinuedDrugOrderValidationMessage && isObservationFormValid();
            };

            var copyConsultationToScope = function (consultationWithDiagnosis) {
                consultationWithDiagnosis.preSaveHandler = $scope.consultation.preSaveHandler;
                consultationWithDiagnosis.postSaveHandler = $scope.consultation.postSaveHandler;
                $scope.$parent.consultation = consultationWithDiagnosis;
                $scope.$parent.consultation.postSaveHandler.fire();
                $scope.dashboardDirty = true;
            };

            var encounterTypeUuid = configurations.encounterConfig().getPatientDocumentEncounterTypeUuid();
            $scope.patientDocumentsPromise = encounterService.getEncountersForEncounterType($scope.patient.uuid, encounterTypeUuid).then(function (response) {
                return new Bahmni.Clinical.PatientFileObservationsMapper().map(response.data.results);
            });

            $scope.save = function (toStateConfig) {
                var storedMessages = JSON.parse(localStorage.getItem('validationMessages') || '[]');
                if (!isFormValid() || storedMessages.length > 0) {
                    if (isFormValid() && storedMessages.length > 0) { messagingService.showMessage("error", "Please correct invalid insertions first!") }
                    $scope.$parent.$parent.$broadcast("event:errorsOnForm");
                    return $q.when({});
                }
                var activeOrders = $scope.consultation.orders && $scope.consultation.orders.filter(function (o) {
                    return !o.isDiscontinued;
                });
                var orderTypeClassMapConfig = appService.getAppDescriptor().getConfig("orderTypeClassMap");
                var orderTypeClassMap = orderTypeClassMapConfig ? orderTypeClassMapConfig.value : {};
                var labConceptClasses = orderTypeClassMap["Lab Samples"] || ["Test", "LabSet", "LabTest"];
                var hasLabOrders = activeOrders && activeOrders.some(function (o) {
                    return !o.isUnavailable && labConceptClasses.indexOf(o.conceptClassName) !== -1;
                });
                if (hasLabOrders && !$scope.consultation.labLocationId) {
                    messagingService.showMessage("error", "Please select a Lab Location before saving orders.");
                    return $q.when({});
                }
                try {
                    var alerts = angular.copy($rootScope.cdssAlerts) || [];
                    var activeAlerts = alerts.filter(function (alert) {
                        return alert.indicator === 'critical' && alert.isActive;
                    });

                    if (activeAlerts && activeAlerts.length > 0) {
                        messagingService.showMessage("error", "{{ 'CDSS_ALERT_SAVE_ERROR' | translate }}");
                        return $q.when({});
                    }

                    if (alerts && alerts.length > 0) {
                        var cdssAlerts = alerts.map(
                            function (cdssAlert) {
                                cdssAlert.isActive = false;
                                return cdssAlert;
                            }
                        );
                        $rootScope.cdssAlerts = cdssAlerts;
                    }
                    preSaveEvents();
                    var originalNewDiagnoses = $scope.consultation.newlyAddedDiagnoses ? $scope.consultation.newlyAddedDiagnoses.slice() : [];
                    return spinner.forPromise($q.all([preSavePromise(),
                    encounterService.getEncounterType($state.params.programUuid, sessionService.getLoginLocationUuid())]).then(function (results) {
                        var encounterData = results[0];
                        encounterData.encounterTypeUuid = results[1].uuid;
                        var params = angular.copy($state.params);
                        params.cachebuster = Math.random();
                        return encounterService.create(encounterData)
                            .then(function (saveResponse) {
                                $state.dirtyConsultationForm = false;
                                $state.orderRemoved = false;
                                $state.orderCreated = false;
                                $scope.$parent.$broadcast("event:changes-saved");
                                var messageParams = {
                                    encounterUuid: saveResponse.data.encounterUuid,
                                    encounterType: saveResponse.data.encounterType
                                };
                                auditLogService.log($scope.patient.uuid, "EDIT_ENCOUNTER", messageParams, "MODULE_LABEL_CLINICAL_KEY");
                                var consultationMapper = new Bahmni.ConsultationMapper(configurations.dosageFrequencyConfig(), configurations.dosageInstructionConfig(),
                                    configurations.consultationNoteConcept(), configurations.labOrderNotesConcept(), $scope.followUpConditionConcept);
                                var consultation = consultationMapper.map(saveResponse.data);
                                consultation.lastvisited = $scope.lastvisited;
                                return consultation;
                            }).then(function (savedConsultation) {
                                return spinner.forPromise(diagnosisService.populateDiagnosisInformation($scope.patient.uuid, savedConsultation, originalNewDiagnoses)
                                    .then(function (consultationWithDiagnosis) {
                                        return saveConditions().then(function (savedConditions) {
                                            consultationWithDiagnosis.conditions = savedConditions;
                                            messagingService.showMessage('info', "{{'CLINICAL_SAVE_SUCCESS_MESSAGE_KEY' | translate}}");
                                        }, function () {
                                            consultationWithDiagnosis.conditions = $scope.consultation.conditions;
                                        }).then(function () {
                                            copyConsultationToScope(consultationWithDiagnosis);
                                            if ($scope.targetUrl) {
                                                return $window.open($scope.targetUrl, "_self");
                                            }
                                            return $state.transitionTo(toStateConfig ? toStateConfig.toState : $state.current, toStateConfig ? toStateConfig.toParams : params, {
                                                inherit: false,
                                                notify: true,
                                                reload: (toStateConfig !== undefined)
                                            });
                                        }).then(function () {
                                            $rootScope.$broadcast('event:save-successful');
                                        });
                                    }));
                            }).catch(function (error) {
                                var message = Bahmni.Clinical.Error.translate(error) || "{{'CLINICAL_SAVE_FAILURE_MESSAGE_KEY' | translate}}";
                                messagingService.showMessage('error', message);
                            });
                    }));
                } catch (error) {
                    var displayErrors = function (error) {
                        if (angular.isArray(error)) {
                            _.each(error, function (errorObj) {
                                messagingService.showMessage('error', errorObj.message || '[ERROR]');
                            });
                        } else {
                            messagingService.showMessage('error', error.message || '[ERROR]');
                        }
                    };
                    return spinner.forPromise(Promise.resolve(displayErrors(error)));
                }
            };

            $scope.$on("patientContext:goToPatientDashboard", function () {
                $scope.gotoPatientDashboard();
            });

            initialize();
        }]);
