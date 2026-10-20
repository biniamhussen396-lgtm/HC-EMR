'use strict';

angular.module('bahmni.registration')
    .controller('SearchPatientController', ['$http', '$rootScope', '$scope', '$location', '$window', 'spinner', 'patientService', 'appService', '$stateParams',
        'messagingService', '$translate', '$filter', '$bahmniCookieStore', 'encounterService', 'visitService', 'auditLogService', 'ngDialog', 'prescriptionService',
        function ($http, $rootScope, $scope, $location, $window, spinner, patientService, appService, $stateParams, messagingService, $translate, $filter, $bahmniCookieStore, encounterService, visitService, auditLogService, ngDialog, prescriptionService) {
            $scope.results = [];
            $scope.extraIdentifierTypes = _.filter($rootScope.patientConfiguration.identifierTypes, function (identifierType) {
                return !identifierType.primary;
            });
            var searching = false;
            var maxAttributesFromConfig = 5;
            const allSearchConfigs = appService.getAppDescriptor().getConfigValue("patientSearch") || {};
            const patientSearchResultOptions = allSearchConfigs.patientSearchResultOptions != null ? allSearchConfigs.patientSearchResultOptions : {};
            const ignoredIdentifiers = new Set(patientSearchResultOptions.ignorePatientIdentifiers || []);
            $scope.showAge = patientSearchResultOptions.showAge != null ? patientSearchResultOptions.showAge : true;
            $scope.showDOB = patientSearchResultOptions.showDOB != null ? patientSearchResultOptions.showDOB : false;
            $scope.extraIdentifierTypes = _.filter($rootScope.patientConfiguration.identifierTypes, function (identifierType) {
                return !identifierType.primary && !ignoredIdentifiers.has(identifierType.name);
            });
            var patientSearchResultConfigs = appService.getAppDescriptor().getConfigValue("patientSearchResults") || {};
            var erTriageVisitTypes = appService.getAppDescriptor().getConfigValue("erTriageVisitTypes")
            maxAttributesFromConfig = !_.isEmpty(allSearchConfigs.programAttributes) ? maxAttributesFromConfig - 1 : maxAttributesFromConfig;

            $scope.getAddressColumnName = function (column) {
                var columnName = "";
                var columnCamelCase = column.replace(/([-_][a-z])/g, function ($1) {
                    return $1.toUpperCase().replace(/[-_]/, '');
                });
                _.each($scope.addressLevels, function (addressLevel) {
                    if (addressLevel.addressField === columnCamelCase) { columnName = addressLevel.name; }
                });
                return columnName;
            };

            var getQueue = function () {
                var params = {
                    q: "emrapi.sqlsearch.triagequeue",
                    v: "full"
                };
                return $http.get('/openmrs/ws/rest/v1/bahmnicore/sql', {
                    method: "GET",
                    params: params,
                    withCredentials: true
                });
            };

            $scope.triageQueue = function () {
                var searchbyid = getQueue().then(queue => queue.data.map(idno => {
                    patientService.search(undefined, idno.identifier, $scope.addressSearchConfig.field,
                        undefined, undefined, undefined, $scope.customAttributesSearchConfig.fields,
                        $scope.programAttributesSearchConfig.field, $scope.searchParameters.programAttributeFieldValue,
                        $scope.addressSearchResultsConfig.fields, $scope.personSearchResultsConfig.fields,
                        $scope.isExtraIdentifierConfigured())
                        .then(function (data) {
                            mapExtraIdentifiers(data);
                            mapCustomAttributesSearchResults(data);
                            mapAddressAttributesSearchResults(data);
                            mapProgramAttributesSearchResults(data);
                            if (idno.started == 1) {
                                angular.forEach(data.pageOfResults, function (result) {
                                    result.row_number = idno.row_number;
                                    result["background-color"] = idno.emergency_color;
                                    $scope.results.push(result);
                                });
                            }
                            $scope.results.sort((a, b) => a.row_number - b.row_number);
                        })
                }))
            }

            var hasSearchParameters = function () {
                return $scope.searchParameters.name.trim().length > 0 ||
                    $scope.searchParameters.addressFieldValue.trim().length > 0 ||
                    $scope.searchParameters.customAttribute.trim().length > 0 ||
                    $scope.searchParameters.programAttributeFieldValue.trim().length > 0;
            };

            var searchBasedOnQueryParameters = function (offset) {
                if (!isUserPrivilegedForSearch()) {
                    showInsufficientPrivMessage();
                    return;
                }
                var searchParameters = $location.search();
                $scope.searchParameters.addressFieldValue = searchParameters.addressFieldValue || '';
                $scope.searchParameters.name = searchParameters.name || '';
                $scope.searchParameters.customAttribute = searchParameters.customAttribute || '';
                $scope.searchParameters.programAttributeFieldValue = searchParameters.programAttributeFieldValue || '';
                $scope.searchParameters.addressSearchResultsConfig = searchParameters.addressSearchResultsConfig || '';
                $scope.searchParameters.personSearchResultsConfig = searchParameters.personSearchResultsConfig || '';

                $scope.searchParameters.registrationNumber = searchParameters.registrationNumber || "";
                if (hasSearchParameters()) {
                    searching = true;
                    var searchPromise = patientService.search(
                        $scope.searchParameters.name,
                        undefined,
                        $scope.addressSearchConfig.field,
                        $scope.searchParameters.addressFieldValue,
                        $scope.searchParameters.customAttribute,
                        offset,
                        $scope.customAttributesSearchConfig.fields,
                        $scope.programAttributesSearchConfig.field,
                        $scope.searchParameters.programAttributeFieldValue,
                        $scope.addressSearchResultsConfig.fields,
                        $scope.personSearchResultsConfig.fields
                    ).then(function (response) {
                        mapExtraIdentifiers(response);
                        mapCustomAttributesSearchResults(response);
                        mapAddressAttributesSearchResults(response);
                        mapProgramAttributesSearchResults(response);
                        return response;
                    });
                    searchPromise['finally'](function () {
                        searching = false;
                    });
                    return searchPromise;
                }
            };
            $scope.convertToTableHeader = function (camelCasedText) {
                return $translate.instant(camelCasedText).replace(/[A-Z]|^[a-z]/g, function (str) {
                    return " " + str.toUpperCase() + "";
                }).trim();
            };

            $scope.getProgramAttributeValues = function (result) {
                var attributeValues = result && result.patientProgramAttributeValue && result.patientProgramAttributeValue[$scope.programAttributesSearchConfig.field];
                var commaSeparatedAttributeValues = "";
                _.each(attributeValues, function (attr) {
                    commaSeparatedAttributeValues = commaSeparatedAttributeValues + attr + ", ";
                });
                return commaSeparatedAttributeValues.substring(0, commaSeparatedAttributeValues.length - 2);
            };

            var mapExtraIdentifiers = function (data) {
                if (data !== "Searching") {
                    _.each(data.pageOfResults, function (result) {
                        result.extraIdentifiers = result.extraIdentifiers && JSON.parse(result.extraIdentifiers);
                    });
                }
            };

            var mapCustomAttributesSearchResults = function (data) {
                if (($scope.personSearchResultsConfig.fields) && data !== "Searching") {
                    _.map(data.pageOfResults, function (result) {
                        result.customAttribute = result.customAttribute && JSON.parse(result.customAttribute);
                    });
                }
            };

            var mapAddressAttributesSearchResults = function (data) {
                if (($scope.addressSearchResultsConfig.fields) && data !== "Searching") {
                    _.map(data.pageOfResults, function (result) {
                        try {
                            result.addressFieldValue = JSON.parse(result.addressFieldValue);
                        } catch (e) {
                        }
                    });
                }
            };

            var mapProgramAttributesSearchResults = function (data) {
                if (($scope.programAttributesSearchConfig.field) && data !== "Searching") {
                    _.map(data.pageOfResults, function (result) {
                        var programAttributesObj = {};
                        var arrayOfStringOfKeysValue = result.patientProgramAttributeValue && result.patientProgramAttributeValue.substring(2, result.patientProgramAttributeValue.length - 2).split('","');
                        _.each(arrayOfStringOfKeysValue, function (keyValueString) {
                            var keyValueArray = keyValueString.split('":"');
                            var key = keyValueArray[0];
                            var value = keyValueArray[1];
                            if (!_.includes(_.keys(programAttributesObj), key)) {
                                programAttributesObj[key] = [];
                                programAttributesObj[key].push(value);
                            } else {
                                programAttributesObj[key].push(value);
                            }
                        });
                        result.patientProgramAttributeValue = programAttributesObj;
                    });
                }
            };
            var searchCliants = function (person_id, person_id_leng) {
                var params = {
                    q: "bahmni.sqlGet.patients",
                    person_id_leng: person_id_leng,
                    ...person_id
                };
                return $http.get('/openmrs/ws/rest/v1/bahmnicore/sql', {
                    method: "GET",
                    params: params,
                    withCredentials: true
                });
            };

            var showSearchResults = function (searchPromise) {
                $scope.noMoreResultsPresent = false;
                if (searchPromise) {
                    searchPromise.then(function (data) {
                        $scope.results = data.pageOfResults;
                        var person_id_leng = $scope.results.length;
                        var person_id_count = 0;
                        var person_id_obj = {};
                        for (let i = 0; i < 51; i++) {
                            person_id_obj["person_id_" + i] = "-1";
                        }
                        $scope.results.some((e) => {
                            if (person_id_count > 51)
                                return true;
                            person_id_obj["person_id_" + person_id_count] = e.personId;
                            person_id_count++;
                        });

                        var patients = searchCliants(person_id_obj, person_id_leng).then(function (response) {
                            $scope.patientDetails = response.data;
                            if ($scope.patientDetails) {
                                for (var i = 0; i < $scope.results.length; i++) {
                                    var result_pdetail = $scope.patientDetails.filter(e => e.person_id == $scope.results[i].personId);
                                    if (result_pdetail.length) {
                                        $scope.results[i].lastVisit = $scope.patientDetails.filter(e => e.person_id == $scope.results[i].personId)[0].lastVisit;
                                    }
                                }
                            }

                            $scope.noResultsMessage = $scope.results.length === 0 ? 'REGISTRATION_NO_RESULTS_FOUND' : null;
                        });
                        if ($scope.results.length != 0)
                            $scope.results.sort(compare);
                    });
                }
            };

            function compare(a, b) {
                // Use toUpperCase() to ignore character casing
                const givenNameA = a.givenName.toUpperCase();
                const givenNameB = b.givenName.toUpperCase();

                let comparison = 0;
                if (givenNameA > givenNameB) {
                    comparison = 1;
                } else if (givenNameA < givenNameB) {
                    comparison = -1;
                }
                return comparison;
            }

            var setPatientIdentifierSearchConfig = function () {
                $scope.patientIdentifierSearchConfig = {};
                $scope.patientIdentifierSearchConfig.show = allSearchConfigs.searchByPatientIdentifier === undefined ? true : allSearchConfigs.searchByPatientIdentifier;
            };

            var setAddressSearchConfig = function () {
                $scope.addressSearchConfig = allSearchConfigs.address || {};
                $scope.addressSearchConfig.show = !_.isEmpty($scope.addressSearchConfig) && !_.isEmpty($scope.addressSearchConfig.field);
                if ($scope.addressSearchConfig.label && !$scope.addressSearchConfig.label) {
                    throw new Error("Search Config label is not present!");
                }
                if ($scope.addressSearchConfig.field && !$scope.addressSearchConfig.field) {
                    throw new Error("Search Config field is not present!");
                }
            };

            var setCustomAttributesSearchConfig = function () {
                var customAttributesSearchConfig = allSearchConfigs.customAttributes;
                $scope.customAttributesSearchConfig = customAttributesSearchConfig || {};
                $scope.customAttributesSearchConfig.show = !_.isEmpty(customAttributesSearchConfig) && !_.isEmpty(customAttributesSearchConfig.fields);
            };

            var setProgramAttributesSearchConfig = function () {
                $scope.programAttributesSearchConfig = allSearchConfigs.programAttributes || {};
                $scope.programAttributesSearchConfig.show = !_.isEmpty($scope.programAttributesSearchConfig.field);
            };

            var sliceExtraColumns = function () {
                var orderedColumns = Object.keys(patientSearchResultConfigs);
                _.each(orderedColumns, function (column) {
                    if (patientSearchResultConfigs[column].fields && !_.isEmpty(patientSearchResultConfigs[column].fields)) {
                        patientSearchResultConfigs[column].fields = patientSearchResultConfigs[column].fields.slice(patientSearchResultConfigs[column].fields, maxAttributesFromConfig);
                        maxAttributesFromConfig -= patientSearchResultConfigs[column].fields.length;
                    }
                });
            };

            var setSearchResultsConfig = function () {
                var resultsConfigNotFound = false;
                if (_.isEmpty(patientSearchResultConfigs)) {
                    resultsConfigNotFound = true;
                    patientSearchResultConfigs.address = { "fields": allSearchConfigs.address ? [allSearchConfigs.address.field] : {} };
                    patientSearchResultConfigs.personAttributes
                        = { fields: allSearchConfigs.customAttributes ? allSearchConfigs.customAttributes.fields : {} };
                } else {
                    if (!patientSearchResultConfigs.address) patientSearchResultConfigs.address = {};
                    if (!patientSearchResultConfigs.personAttributes) patientSearchResultConfigs.personAttributes = {};
                }

                if (patientSearchResultConfigs.address.fields && !_.isEmpty(patientSearchResultConfigs.address.fields)) {
                    patientSearchResultConfigs.address.fields =
                        patientSearchResultConfigs.address.fields.filter(function (item) {
                            return !_.isEmpty($scope.getAddressColumnName(item));
                        });
                }
                if (!resultsConfigNotFound) sliceExtraColumns();
                $scope.personSearchResultsConfig = patientSearchResultConfigs.personAttributes;
                $scope.addressSearchResultsConfig = patientSearchResultConfigs.address;
            };

            var initialize = function () {
                $scope.searchParameters = {};
                $scope.searchActions = appService.getAppDescriptor().getExtensions("org.bahmni.registration.patient.search.result.action");
                setPatientIdentifierSearchConfig();
                setAddressSearchConfig();
                setCustomAttributesSearchConfig();
                setProgramAttributesSearchConfig();
                setSearchResultsConfig();
            };

            var identifyParams = function (querystring) {
                querystring = querystring.substring(querystring.indexOf('?') + 1).split('&');
                var params = {}, pair, d = decodeURIComponent;
                for (var i = querystring.length - 1; i >= 0; i--) {
                    pair = querystring[i].split('=');
                    params[d(pair[0])] = d(pair[1]);
                }
                return params;
            };

            initialize();

            $scope.disableSearchButton = function () {
                return !$scope.searchParameters.firstName && !$scope.searchParameters.fatherName && !$scope.searchParameters.grandFatherName && !$scope.searchParameters.addressFieldValue && !$scope.searchParameters.customAttribute && !$scope.searchParameters.programAttributeFieldValue;
            };

            $scope.$watch(function () {
                return $location.search();
            }, function () {
                showSearchResults(searchBasedOnQueryParameters(0));
            });

            $scope.searchById = function () {
                if (!isUserPrivilegedForSearch()) {
                    showInsufficientPrivMessage();
                    return;
                }
                if (!$scope.searchParameters.registrationNumber) {
                    return;
                }
                $scope.results = [];

                var patientIdentifier = $scope.searchParameters.registrationNumber;

                $location.search({
                    registrationNumber: $scope.searchParameters.registrationNumber,
                    programAttributeFieldName: $scope.programAttributesSearchConfig.field,
                    patientAttributes: $scope.customAttributesSearchConfig.fields,
                    programAttributeFieldValue: $scope.searchParameters.programAttributeFieldValue,
                    addressSearchResultsConfig: $scope.addressSearchResultsConfig.fields,
                    personSearchResultsConfig: $scope.personSearchResultsConfig.fields
                });

                var searchPromise = patientService.search(undefined, patientIdentifier, $scope.addressSearchConfig.field,
                    undefined, undefined, undefined, $scope.customAttributesSearchConfig.fields,
                    $scope.programAttributesSearchConfig.field, $scope.searchParameters.programAttributeFieldValue,
                    $scope.addressSearchResultsConfig.fields, $scope.personSearchResultsConfig.fields,
                    $scope.isExtraIdentifierConfigured())
                    .then(function (data) {
                        mapExtraIdentifiers(data);
                        mapCustomAttributesSearchResults(data);
                        mapAddressAttributesSearchResults(data);
                        mapProgramAttributesSearchResults(data);
                        if (data.pageOfResults.length === 1) {
                            var patient = data.pageOfResults[0];
                            var forwardUrl = appService.getAppDescriptor().getConfigValue("searchByIdForwardUrl") || "/patient/{{patientUuid}}";
                            $location.url(appService.getAppDescriptor().formatUrl(forwardUrl, { 'patientUuid': patient.uuid }));
                        } else if (data.pageOfResults.length > 1) {
                            $scope.results = data.pageOfResults;
                            $scope.noResultsMessage = null;
                        } else {
                            $scope.patientIdentifier = { 'patientIdentifier': patientIdentifier };
                            $scope.noResultsMessage = 'REGISTRATION_LABEL_COULD_NOT_FIND_PATIENT';
                        }
                    });
                spinner.forPromise(searchPromise);
            };
            var isUserPrivilegedForSearch = function () {
                var applicablePrivs = [Bahmni.Common.Constants.viewPatientsPrivilege, Bahmni.Common.Constants.editPatientsPrivilege,
                Bahmni.Common.Constants.addVisitsPrivilege, Bahmni.Common.Constants.deleteVisitsPrivilege];
                var userPrivs = _.map($rootScope.currentUser.privileges, function (privilege) {
                    return privilege.name;
                });
                var result = _.some(userPrivs, function (privName) {
                    return _.includes(applicablePrivs, privName);
                });
                return result;
            };

            var showInsufficientPrivMessage = function () {
                var message = $translate.instant("REGISTRATION_INSUFFICIENT_PRIVILEGE");
                messagingService.showMessage('error', message);
            };

            $scope.loadingMoreResults = function () {
                return searching && !$scope.noMoreResultsPresent;
            };

            $scope.searchPatients = function () {
                if (!isUserPrivilegedForSearch()) {
                    showInsufficientPrivMessage();
                    return;
                }
                var queryParams = {};
                $scope.results = [];
                if ($scope.searchParameters.firstName || $scope.searchParameters.fatherName || $scope.searchParameters.grandFatherName) {
                    queryParams.name = ($scope.searchParameters.firstName || "") + '%' + ($scope.searchParameters.fatherName || "") + '%' + ($scope.searchParameters.grandFatherName || "");
                }
                if ($scope.searchParameters.fatherName) {
                    if ($scope.searchParameters.firstName)
                        if ($scope.searchParameters.grandFatherName)
                            queryParams.name = $scope.searchParameters.firstName + ' ' + $scope.searchParameters.fatherName + ' ' + $scope.searchParameters.grandFatherName;
                        else queryParams.name = $scope.searchParameters.firstName + ' ' + $scope.searchParameters.fatherName;
                    else queryParams.name = $scope.searchParameters.fatherName;
                }
                if ($scope.searchParameters.grandFatherName) {
                    if ($scope.searchParameters.firstName)
                        if ($scope.searchParameters.fatherName)
                            queryParams.name = $scope.searchParameters.firstName + ' ' + $scope.searchParameters.fatherName + ' ' + $scope.searchParameters.grandFatherName;
                        else queryParams.name = $scope.searchParameters.firstName + ' ' + $scope.searchParameters.fatherName;
                    else queryParams.name = $scope.searchParameters.grandFatherName;
                }
                if ($scope.searchParameters.addressFieldValue) {
                    queryParams.addressFieldValue = $scope.searchParameters.addressFieldValue;
                }
                if ($scope.searchParameters.customAttribute && $scope.customAttributesSearchConfig.show) {
                    queryParams.customAttribute = $scope.searchParameters.customAttribute;
                }
                if ($scope.searchParameters.programAttributeFieldValue && $scope.programAttributesSearchConfig.show) {
                    queryParams.programAttributeFieldName = $scope.programAttributesSearchConfig.field;
                    queryParams.programAttributeFieldValue = $scope.searchParameters.programAttributeFieldValue;
                }
                $location.search(queryParams);
            };

            $scope.resultsPresent = function () {
                return angular.isDefined($scope.results) && $scope.results.length > 0;
            };

            $scope.editPatientUrl = function (url, options) {
                var temp = url;
                for (var key in options) {
                    temp = temp.replace("{{" + key + "}}", options[key]);
                }
                return temp;
            };

            $scope.nextPage = function () {
                if ($scope.nextPageLoading) {
                    return;
                }
                $scope.nextPageLoading = true;
                var promise = searchBasedOnQueryParameters($scope.results.length);
                if (promise) {
                    promise.then(function (data) {
                        angular.forEach(data.pageOfResults, function (result) {
                            $scope.results.push(result);
                        });
                        $scope.noMoreResultsPresent = (data.pageOfResults.length === 0);
                        $scope.nextPageLoading = false;
                    }, function () {
                        $scope.nextPageLoading = false;
                    });
                }
            };

            $scope.forPatient = function (patient) {
                $scope.selectedPatient = patient;
                return $scope;
            };

            $scope.doExtensionAction = function (extension) {
                var forwardTo = appService.getAppDescriptor().formatUrl(extension.url, { 'patientUuid': $scope.selectedPatient.uuid });
                if (extension.label === 'Print') {
                    var params = identifyParams(forwardTo);
                    if (params.launch === 'dialog') {
                        var firstChar = forwardTo.charAt(0);
                        var prefix = firstChar === "/" ? "#" : "#/";
                        var hiddenFrame = $("#printPatientFrame")[0];
                        hiddenFrame.src = prefix + forwardTo;
                        hiddenFrame.contentWindow.print();
                    } else {
                        $location.url(forwardTo);
                    }
                } else {
                    $location.url(forwardTo);
                }
            };

            $scope.extensionActionText = function (extension) {
                return $filter('titleTranslate')(extension);
            };

            $scope.isExtraIdentifierConfigured = function () {
                return !_.isEmpty($scope.extraIdentifierTypes);
            };

            //All the codes below this line are added for Existing ER patients for search functionality and to open visit
            var loginLocationUuid = $bahmniCookieStore.get(Bahmni.Common.Constants.locationCookieName).uuid;
            var defaultVisitType = $rootScope.regEncounterConfiguration.getDefaultVisitType(loginLocationUuid);
            $scope.visitControl = new Bahmni.Common.VisitControl(
                $rootScope.regEncounterConfiguration.getVisitTypesAsArray(),
                defaultVisitType, encounterService, $translate, visitService
            );
            //This method open visits for ER patients and redirect them to  ER triage form 
            $scope.startVisitForExistedPatient = function () {
                $scope.selectTriage();
            };
            var closeVisit = function (visitType) {
                if (visitType != undefined) {
                    visitService.endVisit(visitType.uuid).then(function () {
                        var messageParams = { visitUuid: visitType.uuid, visitType: visitType.visitType };
                        auditLogService.log($scope.selectedPatient.uuid, 'CLOSE_VISIT', messageParams, 'MODULE_LABEL_REGISTRATION_KEY');
                    });
                }
            };
            $scope.selectTriage = function () {
                if ($scope.selectedPatient.uuid != undefined) {
                    $scope.selectedPatient.age = parseInt($scope.selectedPatient.age);
                    $scope.dialog = ngDialog.open({
                        template: 'views/selectTriagePopUp.html',
                        className: 'test ngdialog-theme-default',
                        scope: $scope
                    });
                    $('body').addClass('show-controller-back');
                    if ($scope.selectedPatient.gender != "M" && $scope.selectedPatient.age > 10) {
                        $scope.triageType = erTriageVisitTypes.adultFemale;
                    } else if ($scope.selectedPatient.gender != "M" && $scope.selectedPatient.age <= 10) {
                        $scope.triageType = erTriageVisitTypes.pediatricsFemale;
                    }
                    else {
                        if ($scope.selectedPatient.age > 10) {
                            $scope.triageType = erTriageVisitTypes.adultMale;
                        }
                        else if ($scope.selectedPatient.age <= 10) {
                            $scope.triageType = erTriageVisitTypes.pediatricsMale;
                        } else {
                            $scope.triageType = erTriageVisitTypes.Other;
                        }
                    }
                }
            };
            $scope.selectedTriage = function (triageSelected) {
                $scope.triageSelected = triageSelected;
                var selectedVisitType = $scope.visitControl.visitTypes.filter(function (visitType) {
                    return visitType.name === $scope.triageSelected;
                })[0];
                $scope.visitControl.startVisit(selectedVisitType);
                if ($scope.selectedPatient.activeVisitUuid != null) {
                    visitService.getVisitSummary($scope.selectedPatient.activeVisitUuid).then(function (response) {
                        closeVisit(response.data)
                    })
                }
                return spinner.forPromise($scope.visitControl.createVisitOnly($scope.selectedPatient.uuid, $rootScope.visitLocation).then(function (response) {
                    auditLogService.log($scope.selectedPatient.uuid, "OPEN_VISIT", { visitUuid: response.data.uuid, visitType: response.data.visitType.display }, 'MODULE_LABEL_REGISTRATION_KEY');
                    $location.url("/patient/" + $scope.selectedPatient.uuid + "/erTriageVisit/" + $scope.triageSelected);
                    ngDialog.close();
                }))
            }

            //This method open visits for CR patients and redirect them to  ER triage form 
            $scope.startVisitForExistedPatientCR = function () {
                $rootScope.newCRPat = true;
                var selectedVisitType = $scope.visitControl.visitTypes.filter(function (visitType) {
                    return visitType.name === "Central Triage";
                })[0];
                $scope.visitControl.startVisit(selectedVisitType);
                if ($scope.selectedPatient.activeVisitUuid != null) {
                    visitService.getVisitSummary($scope.selectedPatient.activeVisitUuid).then(function (response) {
                        closeVisit(response.data)
                    })
                }
                spinner.forPromise($scope.visitControl.createVisitOnly($scope.selectedPatient.uuid, $rootScope.visitLocation).then(function (response) {
                    auditLogService.log($scope.selectedPatient.uuid, "OPEN_VISIT", { visitUuid: response.data.uuid, visitType: response.data.visitType.display }, 'MODULE_LABEL_REGISTRATION_KEY');
                }));
                $location.url("/patient/" + $scope.selectedPatient.uuid + "/crTriageVisit");

            };
            $scope.prescriptionForExistedPatient = function () {
            $location.url("/patient/" + $scope.selectedPatient.uuid + "/prescription");
                
            };

            $scope.visitControl.onStartVisit = function () {
                //This method should be defined because the super visitControl.startVisit method calls it
            };

            //This method gives search functionality for ER patients
            $scope.searchErPatientsById = function () {
                if (!isUserPrivilegedForSearch()) {
                    showInsufficientPrivMessage();
                    return;
                }
                if (!$scope.searchParameters.registrationNumber) {
                    return;
                }
                $scope.results = [];

                var patientIdentifier = $scope.searchParameters.registrationNumber;

                $location.search({
                    registrationNumber: $scope.searchParameters.registrationNumber,
                    programAttributeFieldName: $scope.programAttributesSearchConfig.field,
                    patientAttributes: $scope.customAttributesSearchConfig.fields,
                    programAttributeFieldValue: $scope.searchParameters.programAttributeFieldValue,
                    addressSearchResultsConfig: $scope.addressSearchResultsConfig.fields,
                    personSearchResultsConfig: $scope.personSearchResultsConfig.fields
                });

                var searchPromise = patientService.search(undefined, patientIdentifier, $scope.addressSearchConfig.field,
                    undefined, undefined, undefined, $scope.customAttributesSearchConfig.fields,
                    $scope.programAttributesSearchConfig.field, $scope.searchParameters.programAttributeFieldValue,
                    $scope.addressSearchResultsConfig.fields, $scope.personSearchResultsConfig.fields,
                    $scope.isExtraIdentifierConfigured())
                    .then(function (data) {
                        mapExtraIdentifiers(data);
                        mapCustomAttributesSearchResults(data);
                        mapAddressAttributesSearchResults(data);
                        mapProgramAttributesSearchResults(data);
                        if (data.pageOfResults.length >= 1) {
                            $scope.results = data.pageOfResults;
                            $scope.noResultsMessage = null;
                        } else {
                            $scope.patientIdentifier = { 'patientIdentifier': patientIdentifier };
                            $scope.noResultsMessage = 'REGISTRATION_LABEL_COULD_NOT_FIND_PATIENT';
                        }
                    });
                spinner.forPromise(searchPromise);
            };

            // Prescribed Patients List functionality
            $scope.showPrescribedList = false;
            $scope.loadingPrescribedPatients = false;
            $scope.prescribedPatients = [];
            $scope.allPrescribedPatients = [];
            $scope.sortColumn = 'prescription_date';
            $scope.sortReverse = true;
            $scope.totalPrescriptionCount = 0;

            $scope.prescriptionFilters = {
                searchText: '',
                startDate: null,
                endDate: null
            };

            $scope.loadAllPrescribedPatients = function () {
                $scope.loadingPrescribedPatients = true;
                $scope.showPrescribedList = true;

                prescriptionService.getAllPrescribedPatients().then(function (response) {
                    $scope.allPrescribedPatients = response.data || [];
                    $scope.applyPrescriptionFilters();
                    $scope.loadingPrescribedPatients = false;
                }).catch(function (error) {
                    console.error("Error loading prescribed patients:", error);
                    messagingService.showMessage('error', "Failed to load prescribed patients!");
                    $scope.loadingPrescribedPatients = false;
                });
            };

            $scope.groupPrescriptionsByDate = function (prescriptions) {
                if (!prescriptions || prescriptions.length === 0) return [];
                var groups = {};
                prescriptions.forEach(function (rx) {
                    var encounterKey = rx.encounter_uuid || 'unknown';
                    var dateKey = 'Unknown Date';
                    var dateDisplay = 'Unknown Date';
                    if (rx.prescription_date) {
                        if (Array.isArray(rx.prescription_date)) {
                            var y = rx.prescription_date[0];
                            var m = String(rx.prescription_date[1]).padStart(2, '0');
                            var d = String(rx.prescription_date[2]).padStart(2, '0');
                            dateKey = y + '-' + m + '-' + d;
                            dateDisplay = d + '/' + m + '/' + y;
                        } else if (typeof rx.prescription_date === 'string') {
                            var parts = rx.prescription_date.split('T')[0].split('-');
                            dateKey = parts[0] + '-' + parts[1] + '-' + parts[2];
                            dateDisplay = parts[2] + '/' + parts[1] + '/' + parts[0];
                        }
                    }
                    var providerKey = rx.provider_name || 'Unknown Provider';
                    if (!groups[encounterKey]) {
                        groups[encounterKey] = {
                            encounter_uuid: encounterKey,
                            date: dateKey,
                            dateDisplay: dateDisplay,
                            provider: providerKey,
                            drugs: []
                        };
                    }
                    groups[encounterKey].drugs.push(rx);
                });
                var result = [];
                Object.keys(groups).forEach(function (key) {
                    result.push(groups[key]);
                });
                result.sort(function (a, b) {
                    return String(b.date).localeCompare(String(a.date));
                });
                return result;
            };

            $scope.applyPrescriptionFilters = function () {
                var searchText = ($scope.prescriptionFilters.searchText || '').toLowerCase();
                var startDate = $scope.prescriptionFilters.startDate ? new Date($scope.prescriptionFilters.startDate) : null;
                var endDate = $scope.prescriptionFilters.endDate ? new Date($scope.prescriptionFilters.endDate) : null;

                if (startDate) startDate.setHours(0, 0, 0, 0);
                if (endDate) endDate.setHours(23, 59, 59, 999);

                var totalCount = 0;

                $scope.prescribedPatients = $scope.allPrescribedPatients.filter(function (patient) {
                    var matchesSearch = true;
                    var matchesDate = true;

                    if (searchText) {
                        matchesSearch = (patient.patient_identifier && patient.patient_identifier.toLowerCase().indexOf(searchText) !== -1) ||
                                        (patient.first_name && patient.first_name.toLowerCase().indexOf(searchText) !== -1) ||
                                        (patient.father_name && patient.father_name.toLowerCase().indexOf(searchText) !== -1) ||
                                        (patient.grandfather_name && patient.grandfather_name.toLowerCase().indexOf(searchText) !== -1) ||
                                        (patient.phone_number && patient.phone_number.toLowerCase().indexOf(searchText) !== -1);

                        if (!matchesSearch && patient.prescriptions) {
                            matchesSearch = patient.prescriptions.some(function (rx) {
                                return (rx.drug_name && rx.drug_name.toLowerCase().indexOf(searchText) !== -1);
                            });
                        }
                    }

                    if (startDate || endDate) {
                        var matchingRx = (patient.prescriptions || []).filter(function (rx) {
                            if (!rx.prescription_date) return false;
                            var rxDate;
                            if (Array.isArray(rx.prescription_date)) {
                                rxDate = new Date(rx.prescription_date[0], rx.prescription_date[1] - 1, rx.prescription_date[2]);
                            } else {
                                rxDate = new Date(rx.prescription_date);
                            }
                            if (isNaN(rxDate.getTime())) return false;
                            if (startDate && rxDate < startDate) return false;
                            if (endDate && rxDate > endDate) return false;
                            return true;
                        });

                        if (matchingRx.length === 0) {
                            matchesDate = false;
                        } else {
                            patient.filteredPrescriptions = matchingRx;
                        }
                    } else {
                        patient.filteredPrescriptions = patient.prescriptions;
                    }

                    if (matchesSearch && matchesDate) {
                        var rxList = patient.filteredPrescriptions || patient.prescriptions || [];
                        totalCount += rxList.length;
                        patient._groupedPrescriptions = $scope.groupPrescriptionsByDate(rxList);
                        return true;
                    }
                    return false;
                });

                $scope.totalPrescriptionCount = totalCount;
            };

            $scope.clearPrescriptionFilters = function () {
                $scope.prescriptionFilters = {
                    searchText: '',
                    startDate: null,
                    endDate: null
                };
                $scope.applyPrescriptionFilters();
            };

            $scope.sortPrescribedPatients = function (column) {
                if ($scope.sortColumn === column) {
                    $scope.sortReverse = !$scope.sortReverse;
                } else {
                    $scope.sortColumn = column;
                    $scope.sortReverse = false;
                }
            };

            $scope.goToPatientPrescription = function (patientUuid) {
                $location.url("/patient/" + patientUuid + "/prescription");
            };

            $scope.goToHistoricalPrescription = function (patientUuid, encounterUuid) {
                $location.url("/patient/" + patientUuid + "/prescription?encounter=" + encounterUuid);
            };
        }]);