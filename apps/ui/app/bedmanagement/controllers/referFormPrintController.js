'use strict';

angular.module('bahmni.ipd')
    .controller('ReferFormPrintController', ['$scope', '$rootScope', '$state', '$stateParams', '$http', '$bahmniCookieStore', 'dispositionService', 'visitService', 'patientService',
        function ($scope, $rootScope, $state, $stateParams, $http, $bahmniCookieStore, dispositionService, visitService, patientService) {
            $scope.currentDate = new Date();
            $scope.patient = $rootScope.patient;
            $scope.patientFullName = '';
            $scope.facilityName = 'Health Facility';
            $scope.facilityLogo = '/bahmni_config/openmrs/apps/home/logo.png';
            $scope.facilityPhone = '';

            var formatFullName = function (personObj) {
                if (!personObj) return '';
                var n = null;
                if (personObj.person && personObj.person.names && personObj.person.names.length > 0) {
                    n = personObj.person.names[0];
                } else if (personObj.names && personObj.names.length > 0) {
                    n = personObj.names[0];
                }
                if (n) {
                    var parts = [n.givenName, n.middleName, n.familyName].filter(Boolean);
                    if (parts.length > 0) return parts.join(' ');
                }
                if (personObj.givenName || personObj.familyName) {
                    var parts = [personObj.givenName, personObj.middleName, personObj.familyName].filter(Boolean);
                    if (parts.length > 0) return parts.join(' ');
                }
                return personObj.name || personObj.display || '';
            };

            // Sync facility name & logo dynamically from system configuration
            $http.get('/bahmni_config/openmrs/apps/home/whiteLabel.json', { ignoreErrors: true }).then(function (response) {
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

            // Initial demographic bindings directly from $stateParams (fallback/immediate render)
            $scope.patientFullName = $stateParams.patientName || '';
            $scope.woreda = $stateParams.woreda || '';
            $scope.kebele = $stateParams.kebele || '';
            $scope.patientIdentifier = $stateParams.identifier || ($rootScope.patient && $rootScope.patient.identifier) || '';
            $scope.patientAge = ($stateParams.age !== undefined && $stateParams.age !== null && $stateParams.age !== '') ? $stateParams.age : ($rootScope.patient && $rootScope.patient.age !== undefined ? $rootScope.patient.age : '');
            var rawSex = $stateParams.sex || ($rootScope.patient && $rootScope.patient.gender) || '';
            $scope.patientSex = (rawSex === 'M' || rawSex === 'Male') ? 'Male' : ((rawSex === 'F' || rawSex === 'Female') ? 'Female' : rawSex);

            if ($scope.patient) {
                $scope.patientFullName = formatFullName($scope.patient) || $scope.patientFullName;
                if ($scope.patient.address) {
                    $scope.woreda = $scope.patient.address.cityVillage || $scope.woreda;
                    $scope.kebele = $scope.patient.address.address2 || $scope.kebele;
                }
                if ($scope.patient.identifier) {
                    $scope.patientIdentifier = $scope.patient.identifier;
                } else if ($scope.patientIdentifier) {
                    $scope.patient.identifier = $scope.patientIdentifier;
                }
                if ($scope.patient.age !== undefined && $scope.patient.age !== null && $scope.patient.age !== '') {
                    $scope.patientAge = $scope.patient.age;
                } else if ($scope.patientAge !== undefined && $scope.patientAge !== null && $scope.patientAge !== '') {
                    $scope.patient.age = $scope.patientAge;
                }
                if ($scope.patient.gender) {
                    var pg = $scope.patient.gender;
                    $scope.patientSex = (pg === 'M' || pg === 'Male') ? 'Male' : ((pg === 'F' || pg === 'Female') ? 'Female' : pg);
                } else if ($scope.patientSex) {
                    $scope.patient.gender = $scope.patientSex;
                }
                if (!$scope.patient.name && $scope.patientFullName) {
                    $scope.patient.name = $scope.patientFullName;
                }
            } else {
                $scope.patient = {
                    identifier: $scope.patientIdentifier,
                    age: $scope.patientAge,
                    gender: $scope.patientSex,
                    name: $scope.patientFullName
                };
            }

            var printUser = $rootScope.currentUser;
            var printUserName = '';
            if (printUser) {
                printUserName = formatFullName(printUser);
                if (!printUserName) {
                    if (printUser.person && printUser.person.display) {
                        printUserName = printUser.person.display;
                    } else if (printUser.provider && printUser.provider.display) {
                        printUserName = printUser.provider.display.replace(/\s*-\s*\d+$/, '').trim();
                    } else if (printUser.provider && printUser.provider.name) {
                        printUserName = printUser.provider.name;
                    } else if (printUser.display) {
                        printUserName = printUser.display;
                    } else if (printUser.username) {
                        printUserName = printUser.username;
                    }
                }
            }

            // Senior Physician Approval details (saved with referral, not default logged-in user)
            $scope.seniorPhysicianApprovedBy = $stateParams.approvedBy || '';
            $scope.seniorPhysicianSpecialty = $stateParams.approvedSpecialty || '';
            $scope.referralApprovalMethod = $stateParams.approvalMethod || '';
            $scope.referralApprovalDateTime = $stateParams.approvalDateTime || '';
            $scope.referralApprovalNotes = $stateParams.approvalNotes || '';

            // Referring Doctor (Referred by row)
            $scope.referringDoctor = $stateParams.physicianName || $stateParams.providerName || '';

            // Liaison Officer (final row)
            $scope.liaisonOfficerName = printUserName || 'Liaison Officer';
            $scope.liaisonOfficerRole = 'Liaison Officer';

            $scope.referralLocation = $stateParams.location || '';
            $scope.referredTo = $stateParams.referredTo || '';
            $scope.referralDepartment = $stateParams.department || '';
            $scope.patientCondition = $stateParams.patientCondition || '';
            $scope.reasonForReferral = $stateParams.reasonForReferral || '';
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
            $scope.referralDiagnosis = $stateParams.diagnosis || '';
            $scope.needAmbulance = $stateParams.needAmbulance || '';
            $scope.needEscorting = $stateParams.needEscorting || '';
            $scope.referralDept = $stateParams.department || '';
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

            var fetchDisposition = function (visitUuid) {
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

                                    // Senior Physician Approval obs
                                    var obsAppr = getObsByName(ref.additionalObs, 'Referral Approved By');
                                    if (obsAppr) $scope.seniorPhysicianApprovedBy = obsAppr;
                                    var obsSpec = getObsByName(ref.additionalObs, 'Referral Senior Physician Specialty');
                                    if (obsSpec) $scope.seniorPhysicianSpecialty = obsSpec;
                                    var obsMethod = getObsByName(ref.additionalObs, 'Referral Approval Method');
                                    if (obsMethod) $scope.referralApprovalMethod = obsMethod;
                                    var obsDt = getObsByName(ref.additionalObs, 'Referral Approval DateTime');
                                    if (obsDt) $scope.referralApprovalDateTime = obsDt;
                                    var obsNotes = getObsByName(ref.additionalObs, 'Referral Approval Notes');
                                    if (obsNotes) $scope.referralApprovalNotes = obsNotes;
                                }
                                if (!$scope.referringDoctor) {
                                    if (ref.creatorName) {
                                        $scope.referringDoctor = ref.creatorName;
                                    } else if (ref.providers && ref.providers.length > 0 && ref.providers[0].name) {
                                        $scope.referringDoctor = ref.providers[0].name;
                                    } else if (ref.additionalObs && ref.additionalObs.length > 0) {
                                        for (var k = 0; k < ref.additionalObs.length; k++) {
                                            if (ref.additionalObs[k].creator && ref.additionalObs[k].creator.personName) {
                                                $scope.referringDoctor = ref.additionalObs[k].creator.personName;
                                                break;
                                            }
                                        }
                                    }
                                }
                                break;
                            }
                        }
                    }
                }).catch(function (err) {
                    // Gracefully continue using parameters passed from register
                });
            };

            // Always fetch complete patient data to guarantee full three names, identifier, age, sex, and address
            if ($stateParams.patientUuid && $stateParams.patientUuid.indexOf('11111111-') === -1) {
                patientService.getPatient($stateParams.patientUuid, 'full', { ignoreErrors: true }).then(function (response) {
                    var rawPatient = (response && response.data) ? response.data : response;
                    if (rawPatient) {
                        var person = rawPatient.person || rawPatient;

                        // 1. Extract Primary Identifier (MRN)
                        var primaryId = '';
                        if (rawPatient.identifiers && rawPatient.identifiers.length > 0) {
                            var pref = rawPatient.identifiers.find(function (id) { return id.preferred; });
                            primaryId = (pref && pref.identifier) || rawPatient.identifiers[0].identifier;
                        } else if (rawPatient.identifier) {
                            primaryId = rawPatient.identifier;
                        } else if (rawPatient.display && rawPatient.display.indexOf(' - ') !== -1) {
                            primaryId = rawPatient.display.split(' - ')[0].trim();
                        }
                        if (primaryId) {
                            $scope.patientIdentifier = primaryId;
                        }

                        // 2. Extract Age
                        var extractedAge = (person.age !== undefined && person.age !== null && person.age !== '') ? person.age : ((rawPatient.age !== undefined && rawPatient.age !== null) ? rawPatient.age : '');
                        if (extractedAge === '' && person.birthdate) {
                            try {
                                var bdate = new Date(person.birthdate);
                                var ageDiff = Date.now() - bdate.getTime();
                                var ageDate = new Date(ageDiff);
                                extractedAge = Math.abs(ageDate.getUTCFullYear() - 1970);
                            } catch (e) {}
                        }
                        if (extractedAge !== '') {
                            $scope.patientAge = extractedAge;
                        }

                        // 3. Extract Gender / Sex
                        var g = person.gender || rawPatient.gender;
                        if (g) {
                            $scope.patientSex = (g === 'M' || g === 'Male') ? 'Male' : ((g === 'F' || g === 'Female') ? 'Female' : g);
                        }

                        // 4. Extract Full Name
                        $scope.patientFullName = formatFullName(rawPatient) || rawPatient.name || $scope.patientFullName;

                        // 5. Extract Address (Woreda, Kebele)
                        var addr = person.preferredAddress || (person.addresses && person.addresses.length > 0 ? person.addresses[0] : rawPatient.address);
                        if (addr) {
                            $scope.woreda = addr.cityVillage || $scope.woreda;
                            $scope.kebele = addr.address2 || $scope.kebele;
                        }

                        // Sync $scope.patient object for any template bindings
                        $scope.patient = {
                            uuid: rawPatient.uuid,
                            identifier: $scope.patientIdentifier,
                            age: $scope.patientAge,
                            gender: $scope.patientSex,
                            name: $scope.patientFullName,
                            address: addr
                        };
                    }
                }).catch(function (err) {
                    // Gracefully continue using initial patient data
                });
            }

            if ($stateParams.visitUuid) {
                if ($stateParams.visitUuid.indexOf('22222222-') === -1) {
                    fetchDisposition($stateParams.visitUuid);
                }
            } else if ($stateParams.patientUuid && $stateParams.patientUuid.indexOf('11111111-') === -1) {
                $http.get(Bahmni.Common.Constants.visitUrl, {
                    params: { patient: $stateParams.patientUuid, includeInactive: true, v: 'custom:(uuid)' },
                    withCredentials: true,
                    ignoreErrors: true
                }).then(function (visitsResponse) {
                    var results = visitsResponse.data.results;
                    if (results && results.length > 0) {
                        var visitUuid = results[results.length - 1].uuid;
                        fetchDisposition(visitUuid);
                    }
                }).catch(function (err) {
                    // Gracefully continue
                });
            }

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
