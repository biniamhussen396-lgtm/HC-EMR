'use strict';

angular.module('bahmni.ipd')
    .controller('ReferFormPrintController', ['$scope', '$rootScope', '$state', '$stateParams', '$http', '$bahmniCookieStore', 'dispositionService', 'visitService',
        function ($scope, $rootScope, $state, $stateParams, $http, $bahmniCookieStore, dispositionService, visitService) {
            $scope.currentDate = new Date();
            $scope.patient = $rootScope.patient;
            $scope.facilityName = 'Health Facility';
            $scope.facilityLogo = '/bahmni_config/openmrs/apps/home/logo.png';
            $scope.facilityPhone = '';

            // Sync facility name & logo dynamically from system configuration
            $http.get('/bahmni_config/openmrs/apps/home/whiteLabel.json').then(function (response) {
                if (response.data && response.data.homePage) {
                    if (response.data.homePage.logo) {
                        $scope.facilityLogo = response.data.homePage.logo;
                    }
                    if (response.data.homePage.header_text) {
                        var temp = document.createElement('div');
                        temp.innerHTML = response.data.homePage.header_text;
                        var raw = (temp.textContent || temp.innerText || '').trim();
                        raw = raw.replace(/^WELCOME\s*TO\s*/i, '')
                                 .replace(/\s*EMR\s*System\s*$/i, '')
                                 .replace(/\s*EMR\s*$/i, '')
                                 .trim();
                        if (raw) {
                            $scope.facilityName = raw;
                        }
                    }
                }
                var locCookie = $bahmniCookieStore && $bahmniCookieStore.get(Bahmni.Common.Constants.locationCookieName);
                if ((!$scope.facilityName || $scope.facilityName === 'Health Facility') && locCookie && locCookie.name) {
                    $scope.facilityName = locCookie.name;
                }
            }).catch(function () {
                var locCookie = $bahmniCookieStore && $bahmniCookieStore.get(Bahmni.Common.Constants.locationCookieName);
                if (locCookie && locCookie.name) {
                    $scope.facilityName = locCookie.name;
                }
            });
            $scope.woreda = '';
            $scope.kebele = '';
            if ($scope.patient && $scope.patient.address) {
                $scope.woreda = $scope.patient.address.cityVillage || '';
                $scope.kebele = $scope.patient.address.address2 || '';
            }
            var user = $rootScope.currentUser;
            var doctorName = '';
            if (user) {
                if (user.provider && user.provider.display) {
                    doctorName = user.provider.display.replace(/\s*-\s*\d+$/, '').trim();
                }
                if (!doctorName && user.provider && user.provider.name) {
                    doctorName = user.provider.name;
                }
                if (!doctorName) {
                    doctorName = user.username;
                }
            }
            $scope.referringDoctor = doctorName;
            $scope.referredTo = '';
            $scope.referralDepartment = '';
            $scope.patientCondition = '';
            $scope.reasonForReferral = '';
            $scope.clinicalHistory = '';
            $scope.treatmentProvided = '';
            $scope.chiefComplaint = '';
            $scope.historyOfPresentIllness = '';
            $scope.systolicBP = '';
            $scope.diastolicBP = '';
            $scope.pulseRate = '';
            $scope.respiratoryRate = '';
            $scope.bodyTemperature = '';
            $scope.oxygenSaturation = '';
            $scope.onOxygen = '';
            $scope.labResult = '';
            $scope.referralDiagnosis = '';
            $scope.needAmbulance = '';
            $scope.needEscorting = '';
            $scope.referralDept = '';
            var activeVisitUuid = null;

            var getObsByName = function (obs, name) {
                if (!obs || !name) return '';
                for (var j = 0; j < obs.length; j++) {
                    if (obs[j].concept) {
                        var conceptName = '';
                        if (typeof obs[j].concept.name === 'string') {
                            conceptName = obs[j].concept.name;
                        } else if (obs[j].concept.name && obs[j].concept.name.name) {
                            conceptName = obs[j].concept.name.name;
                        } else if (obs[j].concept.display) {
                            conceptName = obs[j].concept.display;
                        }
                        if (conceptName === name) {
                            return obs[j].value;
                        }
                    }
                }
                return '';
            };

            visitService.search({patient: $stateParams.patientUuid, includeInactive: false, v: 'custom:(uuid)'}).then(function (visitsResponse) {
                var results = visitsResponse.data.results;
                if (results && results.length > 0) {
                    var visitUuid = results[results.length - 1].uuid;
                    activeVisitUuid = visitUuid;
                    dispositionService.getDispositionByVisit(visitUuid).then(function (response) {
                        var dispositions = response.data;
                        if (dispositions && dispositions.length > 0) {
                            for (var i = 0; i < dispositions.length; i++) {
                                if (dispositions[i].code === Bahmni.Common.Constants.referCode) {
                                    var ref = dispositions[i];
                                    if (ref.additionalObs) {
                                        $scope.referredTo = getObsByName(ref.additionalObs, 'Refers');
                                        $scope.referralDepartment = getObsByName(ref.additionalObs, 'Referral department');
                                        $scope.patientCondition = getObsByName(ref.additionalObs, 'Patient condition at referral');
                                        $scope.reasonForReferral = getObsByName(ref.additionalObs, 'Reason for referral (text)');
                                        $scope.clinicalHistory = getObsByName(ref.additionalObs, 'Relevant clinical history');
                                        $scope.treatmentProvided = getObsByName(ref.additionalObs, 'Treatment provided');
                                        $scope.chiefComplaint = getObsByName(ref.additionalObs, 'Chief complaint (text)');
                                        $scope.historyOfPresentIllness = getObsByName(ref.additionalObs, 'History of present illness');
                                        $scope.systolicBP = getObsByName(ref.additionalObs, 'Systolic blood pressure');
                                        $scope.diastolicBP = getObsByName(ref.additionalObs, 'Diastolic blood pressure');
                                        $scope.pulseRate = getObsByName(ref.additionalObs, 'Pulse');
                                        $scope.respiratoryRate = getObsByName(ref.additionalObs, 'Respiratory rate');
                                        $scope.bodyTemperature = getObsByName(ref.additionalObs, 'Temperature');
                                        $scope.oxygenSaturation = getObsByName(ref.additionalObs, 'Arterial blood oxygen saturation (pulse oximeter)');
                                        $scope.onOxygen = getObsByName(ref.additionalObs, 'BMH On Oxygen');
                                        $scope.labResult = getObsByName(ref.additionalObs, 'Lab results (text)');
                                        $scope.referralDiagnosis = getObsByName(ref.additionalObs, 'Non-coded Diagnosis');
                                        $scope.needAmbulance = getObsByName(ref.additionalObs, 'Need ambulance');
                                        $scope.needEscorting = getObsByName(ref.additionalObs, 'Need escorting professionals');
                                        $scope.referralDept = getObsByName(ref.additionalObs, 'Referral department');
                                    }
                                    break;
                                }
                            }
                        }
                    });
                }
            });

            $scope.printForm = function () {
                window.print();
            };

            $scope.closeForm = function () {
                if (activeVisitUuid) {
                    visitService.endVisit(activeVisitUuid).then(function () {
                        $rootScope.toReferTab = true;
                        $state.go('home');
                    });
                } else {
                    $rootScope.toReferTab = true;
                    $state.go('home');
                }
            };
        }
    ]);
