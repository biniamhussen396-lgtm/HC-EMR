'use strict';

angular.module('bahmni.common.patientSearch')
.controller('PatientsListController', ['$scope', '$window', 'patientService', '$rootScope', 'appService', 'spinner',
    '$stateParams', '$bahmniCookieStore', 'printer', 'configurationService', '$timeout', 'observationsService', '$injector',
    function ($scope, $window, patientService, $rootScope, appService, spinner, $stateParams, $bahmniCookieStore, printer, configurationService, $timeout, observationsService, $injector) {
        var dispositionService = $injector.has('dispositionService') ? $injector.get('dispositionService') : null;
        $scope.preferExtraIdInSearchResults = appService.getAppDescriptor().getConfigValue("preferExtraIdInSearchResults");
        $scope.activeHeaders = [];
        const DEFAULT_FETCH_DELAY = 2000;
        var patientSearchConfig = appService.getAppDescriptor().getConfigValue("patientSearch");
        var patientListSpinner;
        $scope.triageStatus = "#88af28";
        var initialize = function () {
            var searchTypes = appService.getAppDescriptor().getExtensions("org.bahmni.patient.search", "config").map(mapExtensionToSearchType);
            $scope.ignoredTabularViewHeadingsConfig = appService.getAppDescriptor().getConfigValue("ignoredTabularViewHeadings") || [];
            $scope.identifierHeadingsConfig = appService.getAppDescriptor().getConfigValue("identifierHeadings") || [];
            $scope.search = new Bahmni.Common.PatientSearch.Search(_.without(searchTypes, undefined));
            $scope.search.markPatientEntry();
            $scope.$watch('search.searchType', function (currentSearchType) {
                _.isEmpty(currentSearchType) || fetchPatients(currentSearchType);
            });
            $scope.$watch('search.activePatients', function (activePatientsList) {
                if (activePatientsList.length > 0 && patientListSpinner) {
                    hideSpinner(spinner, patientListSpinner, $(".tab-content"));
                }
            });
            $scope.$watch('search.visiblePatients', function (activePatientsList) {
                if (activePatientsList && activePatientsList.length > 0) {
                    $scope.getHeadings();
                }
                else {
                    if ($scope.activeHeaders.length != 0) {
                        $scope.activeHeaders = [];
                    }
                }
            });
            if (patientSearchConfig && patientSearchConfig.serializeSearch) {
                getPatientCountSeriallyBySearchIndex(0);
            }
            else {
                _.each($scope.search.searchTypes, function (searchType) {
                    _.isEmpty(searchType) || ($scope.search.searchType != searchType && getPatientCount(searchType, null));
                });
            }
            if ($rootScope.currentSearchType != null) {
                $scope.search.switchSearchType($rootScope.currentSearchType);
            }
            if ($rootScope.toReferTab) {
                $rootScope.toReferTab = false;
                var referSearchType = _.find($scope.search.searchTypes, function (st) {
                    return st && st.id === 'bahmni.adt.patients.search.patientsToRefer';
                });
                if (referSearchType) {
                    $scope.search.switchSearchType(referSearchType);
                }
            }
            configurationService.getConfigurations(['identifierTypesConfig']).then(function (response) {
                $scope.primaryIdentifier = _.find(response.identifierTypesConfig, {primary: true}).name;
            }); 
        };
        $scope.start = function(patient){
            if(patient!=undefined){
                patient.triageStatus = "#88af28";
                if(patient.hasBeenAdmitted == "true"){
                    observationsService.fetch(patient.uuid, "Triage Color Result").then(function (response) {
                        if(response.data.length!=0){
                            patient.triageStatus = response.data[0].value;
                        }
                    });
                }
                if(patient.activeVisitUuid && dispositionService){
                    dispositionService.getDispositionByVisit(patient.activeVisitUuid).then(function (response) {
                        var dispositions = response.data;
                        if(dispositions && dispositions.length > 0){
                            for(var i = 0; i < dispositions.length; i++){
                                if(dispositions[i].code === Bahmni.Common.Constants.emergencyKeepCode){
                                    patient.isEmergencyKeep = true;
                                }
                                if(dispositions[i].code === Bahmni.Common.Constants.referCode){
                                    patient.isRefer = true;
                                }
                                if(patient.isEmergencyKeep || patient.isRefer) break;
                            }
                        }
                    });
                }
            }
        }
        $scope.style = function(patient){
            return { "background-color": patient.triageStatus };
        }

        $scope.searchPatients = function () {
            return spinner.forPromise(patientService.search($scope.search.searchParameter)).then(function (response) {
                $scope.search.updateSearchResults(response.data.pageOfResults);
                if ($scope.search.hasSingleActivePatient()) {
                    $scope.forwardPatient($scope.search.activePatients[0]);
                }
            });
        };

        $scope.filterPatientsAndSubmit = function () {
            if ($scope.search.searchResults.length == 1) {
                $scope.forwardPatient($scope.search.searchResults[0]);
            }
        };
        var getPatientCount = function (searchType, patientListSpinner) {
            $scope.ptLocation=$bahmniCookieStore.get(Bahmni.Common.Constants.locationCookieName) ? $bahmniCookieStore.get(Bahmni.Common.Constants.locationCookieName) : null;
            if (searchType.handler) {
                var params = { q: searchType.handler, v: "full",
                    location_uuid: $bahmniCookieStore.get(Bahmni.Common.Constants.locationCookieName).uuid,
                    provider_uuid: $rootScope.currentProvider.uuid };
                if (searchType.additionalParams) {
                    params["additionalParams"] = searchType.additionalParams;
                }
                patientService.findPatients(params).then(function (response) {
                    searchType.patientCount = response.data.length;
                    if ($scope.search.isSelectedSearch(searchType)) {
                        $scope.search.updatePatientList(response.data);
                    }
                    updateNotifications(searchType, response.data);
                    if (patientListSpinner) {
                        hideSpinner(spinner, patientListSpinner, $(".tab-content"));
                    }
                });
            }
        };

        var hideSpinner = function (spinnerObj, data, container) {
            spinnerObj.hide(data, container);
            $(container).children('patient-list-spinner').hide();
        };

        $scope.getHeadings = function () {
            if ($scope.search.activePatients && $scope.search.activePatients.length > 0) {
                var headings = _.chain($scope.search.activePatients[0])
                    .keys()
                    .filter(function (heading) {
                        return _.indexOf($scope.ignoredTabularViewHeadingsConfig, heading) === -1;
                    })
                    .value();
                setActiveHeadings(headings);
            }
        };

        var setActiveHeadings = function (headings) {
            headings.map(function (heading) {
                var newHeading = { name: heading, sortInfo: heading };
                if (!$scope.activeHeaders.find(function (activeHeader) {
                    return activeHeader.name == newHeading.name && activeHeader.sortInfo == newHeading.sortInfo;
                })) {
                    $scope.activeHeaders.push(newHeading);
                }
            });
        };

        $scope.sortVisiblePatientsBy = function (sortColumn) {
            var emptyObjects = _.filter($scope.search.searchResults, function (visiblePatient) {
                return !_.property(sortColumn)(visiblePatient);
            });

            var nonEmptyObjects = _.difference($scope.search.searchResults, emptyObjects);
            var sortedNonEmptyObjects = _.sortBy(nonEmptyObjects, function (visiblePatient) {
                var value = _.get(visiblePatient, sortColumn);
                if (!isNaN(Date.parse(value))) {
                    var parsedDate = moment(value, Bahmni.Common.Constants.clientDateDisplayFormat + " " + Bahmni.Common.Constants.timeDisplayFormat);
                    if (parsedDate.isValid()) {
                        return parsedDate.toDate().getTime();
                    }
                }
                else if (angular.isNumber(value)) {
                    return value;
                }
                else if (angular.isString(value)) {
                    return value.toLowerCase();
                }
                return value;
            });
            if ($scope.reverseSort) {
                sortedNonEmptyObjects.reverse();
            }
            $scope.search.visiblePatients = sortedNonEmptyObjects.concat(emptyObjects);
            $scope.sortColumn = sortColumn;
            $scope.reverseSort = !$scope.reverseSort;
        };

        $scope.isHeadingOfLinkColumn = function (heading) {
            var identifierHeading = _.includes($scope.identifierHeadingsConfig, heading);
            if (identifierHeading) {
                return identifierHeading;
            } else if ($scope.search.searchType && $scope.search.searchType.links) {
                return _.find($scope.search.searchType.links, {linkColumn: heading});
            }
            else if ($scope.search.searchType && $scope.search.searchType.linkColumn) {
                return _.includes([$scope.search.searchType.linkColumn], heading);
            }
        };
        $scope.isHeadingOfName = function (heading) {
            return _.includes(Bahmni.Common.PatientSearch.Constants.nameHeading, heading);
        };
        $scope.getPrintableHeadings = function () {
            $scope.getHeadings();
            var printableHeadings = $scope.activeHeaders.filter(function (heading) {
                return _.indexOf(Bahmni.Common.PatientSearch.Constants.printIgnoreHeadingsList, heading.name) === -1;
            });
            return printableHeadings;
        };
        $scope.printPage = function () {
            if ($scope.search.searchType.printHtmlLocation != null) {
                printer.printFromScope($scope.search.searchType.printHtmlLocation, $scope);
            }
        };

        $scope.iconAttributeConfig = appService.getAppDescriptor().getConfigValue('iconAttribute') || {};

        var mapExtensionToSearchType = function (appExtn) {
            return {
                name: appExtn.label,
                display: appExtn.extensionParams.display,
                handler: appExtn.extensionParams.searchHandler,
                forwardUrl: appExtn.extensionParams.forwardUrl,
                targetedTab: appExtn.extensionParams.targetedTab || null,
                id: appExtn.id,
                params: appExtn.extensionParams.searchParams,
                refreshTime: appExtn.extensionParams.refreshTime || 0,
                view: appExtn.extensionParams.view || Bahmni.Common.PatientSearch.Constants.searchExtensionTileViewType,
                showPrint: appExtn.extensionParams.showPrint || false,
                printHtmlLocation: appExtn.extensionParams.printHtmlLocation || null,
                additionalParams: appExtn.extensionParams.additionalParams,
                searchColumns: appExtn.extensionParams.searchColumns,
                translationKey: appExtn.extensionParams.translationKey,
                descriptionKey: appExtn.extensionParams.descriptionKey,
                linkColumn: appExtn.extensionParams.linkColumn,
                links: appExtn.extensionParams.links,
                templateUrl: appExtn.extensionParams.templateUrl || null
            };
        };

        var debounceGetPatientCount = _.debounce(function (currentSearchType, patientListSpinner) {
            getPatientCount(currentSearchType, patientListSpinner);
        }, (patientSearchConfig && patientSearchConfig.fetchDelay) || DEFAULT_FETCH_DELAY, {});

        var showSpinner = function (spinnerObj, container) {
            $(container).children('patient-list-spinner').show();
            return spinnerObj.show(container);
        };

        var fetchPatients = function (currentSearchType) {
            if (patientListSpinner !== undefined) {
                hideSpinner(spinner, patientListSpinner, $(".tab-content"));
            }
            $rootScope.currentSearchType = currentSearchType;
            if ($scope.search.isCurrentSearchLookUp()) {
                patientListSpinner = showSpinner(spinner, $(".tab-content"));
                if (patientSearchConfig && patientSearchConfig.debounceSearch) {
                    debounceGetPatientCount(currentSearchType, patientListSpinner);
                }
                else {
                    getPatientCount(currentSearchType, patientListSpinner);
                }
            }
        };

        $scope.forwardPatient = function (patient, heading) {
            var options = $.extend({}, $stateParams);
            $rootScope.patientAdmitLocationStatus = patient.Status;
            $.extend(options, {
                patientUuid: patient.uuid,
                visitUuid: patient.activeVisitUuid || null,
                encounterUuid: $stateParams.encounterUuid || 'active',
                programUuid: patient.programUuid || null,
                enrollment: patient.enrollment || null,
                forwardUrl: patient.forwardUrl || null,
                dateEnrolled: patient.dateEnrolled || null
            });
            var link = options.forwardUrl ? {
                url: options.forwardUrl,
                newTab: true
            } : {url: $scope.search.searchType.forwardUrl, newTab: false};
            if ($scope.search.searchType.links) {
                link = _.find($scope.search.searchType.links, {linkColumn: heading}) || _.find($scope.search.searchType.links, { linkColumn: heading.name }) || link;
            }
            if ($scope.search.searchType.targetedTab) {
                link.targetedTab = $scope.search.searchType.targetedTab;
            }
            if (link.url && link.url !== null) {
                var redirectUrl = link.url;
                if (typeof link.url === 'object') {
                    const rowName = patient[heading.name] ? patient[heading.name].replace(/\s/g, "").toLowerCase() : "";
                    redirectUrl = rowName && link.url[rowName] ? link.url[rowName] : link.url.default;
                }
                var newWindow = $window.open(
                appService.getAppDescriptor().formatUrl(redirectUrl, options, true),
                link.newTab ? '_blank' : link.targetedTab ? link.targetedTab : '_self');
                if (link.targetedTab) {
                    $timeout(function () {
                        newWindow.document.title = link.targetedTab;
                        newWindow.location.reload();
                    }, 1000);
                }
            }
        };
        var updateNotifications = function (searchType, data) {
            if (searchType.id == "bahmni.clinical.patients.search.linkedPatients") {
                if (searchType.patientCount > 0) {
                    $rootScope.linkedExists = true;
                    $rootScope.linkNotCount = searchType.patientCount;
                    $scope.linkageNotifications = data;
                }
            }
            if (searchType.id == "bahmni.clinical.patients.search.PatientsWithLabresult") {
                if (searchType.patientCount > 0) {
                    $rootScope.labResultExists = true;
                    $rootScope.labNotCount = searchType.patientCount;
                    $scope.labResultNotifications = data;
                }
            }
            if (searchType.id == "bahmni.clinical.patients.search.PatientsWithRadiologyresult") {
                if (searchType.patientCount > 0) {
                    $rootScope.radResultExists = true;
                    $rootScope.radNotCount = searchType.patientCount;
                    $scope.radResultNotifications = data;
                }
            }
            if (searchType.id == "bahmni.clinical.patients.search.PatientsWithPathologyresult") {
                if (searchType.patientCount > 0) {
                    $rootScope.patResultExists = true;
                    $rootScope.patNotCount = searchType.patientCount;
                    $scope.patResultNotifications = data;
                }
            }
            if (searchType.id == "bahmni.clinical.patients.search.PatientsWithProcedureresult") {
                if (searchType.patientCount > 0) {
                    $rootScope.procResultExists = true;
                    $rootScope.procNotCount = searchType.patientCount;
                    $scope.pocResultNotifications = data;
                }
            }
            if (searchType.id == "bahmni.clinical.patients.search.dtpCases") {
                if (searchType.patientCount > 0) {
                    $rootScope.dtpCaseExists = true;
                    $rootScope.dtpNotCount = searchType.patientCount;
                    $scope.dtpCaseNotifications = data;
                }
            }
        };

        var getPatientCountSeriallyBySearchIndex = function (index) {
            if (index === $scope.search.searchTypes.length) {
                return;
            }
            var searchType = $scope.search.searchTypes[index];
            if (searchType.handler) {
                var params = {
                    q: searchType.handler,
                    v: "full",
                    location_uuid: $bahmniCookieStore.get(Bahmni.Common.Constants.locationCookieName).uuid,
                    provider_uuid: $rootScope.currentProvider.uuid
                };
                if (searchType.additionalParams) {
                    params["additionalParams"] = searchType.additionalParams;
                }
                patientService.findPatients(params).then(function (response) {
                    searchType.patientCount = response.data.length;
                    if ($scope.search.isSelectedSearch(searchType)) {
                        $scope.search.updatePatientList(response.data);
                    }
                    updateNotifications(searchType, response.data);
                    return getPatientCountSeriallyBySearchIndex(index + 1);
                });
            }
        };
        initialize();
    }
]);
