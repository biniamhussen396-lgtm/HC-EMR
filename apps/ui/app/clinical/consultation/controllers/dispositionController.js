'use strict';

angular.module('bahmni.clinical')
    .controller('DispositionController', ['$scope', '$state', '$q', '$http', '$location', 'providerService', 'patientService', 'visitService', 'dispositionService', 'appService', 'messagingService', 'retrospectiveEntryService', 'spinner', '$rootScope', '$translate', async function ($scope, $state, $q, $http, $location, providerService, patientService, visitService, dispositionService, appService, messagingService, retrospectiveEntryService, spinner, $rootScope, $translate) {
        var consultation = $scope.consultation;
        var allDispositions = [];
        var wards = $http.get(Bahmni.Common.Constants.admissionLocationUrl);
        var visitTypes = $http.get(Bahmni.Common.Constants.visitTypeUrl);

        $scope.patient = {};
        $scope.wards = [];
        $scope.visitTypes = [];
        $scope.femaleOnlyVisitTypes = [];
        $scope.femaleVisitTypeNames;

        function extractPatientUUID() {
            const fragmentIdentifier = window.location.hash.replace(/^#/, '');
            const match = fragmentIdentifier.match(/\/patient\/([^/]+)\//);
            return match?.[1];
        }

        $scope.patientUuid = extractPatientUUID();
        patientService.getPatient($scope.patientUuid).then(function (response) {
            $scope.patient = response.data;
        });

        var getFemaleOnlyVisitTypes = function () {
            var params = {
                q: "emrapi.visitTypes.femaleOnlyVisitTypes"
            }
            return $http.get('/openmrs/ws/rest/v1/bahmnicore/sql', {
                method: "GET",
                params: params,
                withCredentials: true
            });
        };

        var getPediOnlyVisitTypes = function () {
            var params = {
                q: "emrapi.visitTypes.pediOnlyVisitTypes"
            }
            return $http.get('/openmrs/ws/rest/v1/bahmnicore/sql', {
                method: "GET",
                params: params,
                withCredentials: true
            });
        };

        var loadAllWards = function () {
            return wards.success(function (wardList) {
                const exist = $scope.patient.person;
                if (exist && $scope.patient.person.age <= 18 && $scope.patient.person.gender === 'M') {
                    $scope.wards = wardList.results
                        .filter(e => !$scope.femaleVisitTypeNames.includes(e.ward.name))
                        .map(e => e.ward.name);
                } else if (exist && $scope.patient.person.age > 18 && $scope.patient.person.gender === 'M') {
                    $scope.wards = wardList.results
                        .filter(e => !$scope.femaleVisitTypeNames.includes(e.ward.name) && !$scope.pediVisitTypeNames.includes(e.ward.name))
                        .map(e => e.ward.name);
                } else if (exist && $scope.patient.person.age > 18 && $scope.patient.person.gender === 'F') {
                    $scope.wards = wardList.results
                        .filter(e => !$scope.pediVisitTypeNames.includes(e.ward.name))
                        .map(e => e.ward.name);
                } else {
                    $scope.wards = wardList.results.map(e => e.ward.name);
                }

            });
        };

        Promise.all([
            getFemaleOnlyVisitTypes().then(response => {
                $scope.femaleOnlyVisitTypes = response.data;
                $scope.femaleVisitTypeNames = $scope.femaleOnlyVisitTypes.map(type => type.name);
            }),
            getPediOnlyVisitTypes().then(response => {
                $scope.pediOnlyVisitTypes = response.data;
                $scope.pediVisitTypeNames = $scope.pediOnlyVisitTypes.map(type => type.name);
            }),
            patientService.getPatient($scope.patientUuid).then(response => {
                $scope.patient = response.data;
            }),
            visitTypes, // If needed, you can process visitTypes after
        ]).then(() => {
            loadAllWards(); // Load wards only after all above are resolved
        });


        $scope.provider = function () {
            var params = { v: "custom:(display,person,uuid,retired,attributes:(attributeType:(display),value,voided))" };
            return providerService.searchAllDoctors(params).then(function (response) {
                $scope.allDoctors = response.data;
                $scope.currentDoctors = $scope.allDoctors;
                if (typeof buildSeniorPhysiciansList === 'function') {
                    buildSeniorPhysiciansList();
                }
            }),
                providerService.searchSpecialists(params).then(function (response) {
                    $scope.specialistProviders = response.data;
                }),
                providerService.searchResidents(params).then(function (response) {
                    $scope.residentProviders = response.data;
                });
        };
        await $scope.provider();
        $scope.selectedProvider = function (selectedSpecialty) {
            $scope.selectedSpecialty = selectedSpecialty;
            $scope.doctors = [];
            if (!$scope.selectedSpecialty && $scope.specialist == true) {
                $scope.currentDoctors = $scope.specialistProviders;
            }
            else if (!$scope.selectedSpecialty && $scope.resident == true) {
                $scope.currentDoctors = $scope.residentProviders;
            }
            else if ($scope.selectedSpecialty && $scope.specialist == true) {
                for (var i = 0; i < $scope.allDoctors.length; i++) {
                    for (var j = 0; j < $scope.specialistProviders.length; j++) {
                        if ($scope.allDoctors[i].role == "Radiology" && $scope.selectedSpecialty == "Radiology") {
                            if ($scope.allDoctors[i].user_id == $scope.specialistProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Dentistry" && $scope.selectedSpecialty == "Dentistry") {
                            if ($scope.allDoctors[i].user_id == $scope.specialistProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Anesthesiology" && $scope.selectedSpecialty == "Anesthesiology") {
                            if ($scope.allDoctors[i].user_id == $scope.specialistProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Dermatovenerology" && $scope.selectedSpecialty == "Dermatovenerology") {
                            if ($scope.allDoctors[i].user_id == $scope.specialistProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "EMCC" && $scope.selectedSpecialty == "EMCC") {
                            if ($scope.allDoctors[i].user_id == $scope.specialistProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "ENT" && $scope.selectedSpecialty == "ENT") {
                            if ($scope.allDoctors[i].user_id == $scope.specialistProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Internal Medicine" && $scope.selectedSpecialty == "Internal Medicine") {
                            if ($scope.allDoctors[i].user_id == $scope.specialistProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Neurology" && $scope.selectedSpecialty == "Neurology") {
                            if ($scope.allDoctors[i].user_id == $scope.specialistProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "OBGYN" && $scope.selectedSpecialty == "OBGYN") {
                            if ($scope.allDoctors[i].user_id == $scope.specialistProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Occupational Therapy" && $scope.selectedSpecialty == "Occupational Therapy") {
                            if ($scope.allDoctors[i].user_id == $scope.specialistProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "OMF Surgery" && $scope.selectedSpecialty == "OMF Surgery") {
                            if ($scope.allDoctors[i].user_id == $scope.specialistProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Ophthalmology" && $scope.selectedSpecialty == "Ophthalmology") {
                            if ($scope.allDoctors[i].user_id == $scope.specialistProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Optometry" && $scope.selectedSpecialty == "Optometry") {
                            if ($scope.allDoctors[i].user_id == $scope.specialistProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Orthopedic & Trauma" && $scope.selectedSpecialty == "Orthopedic & Trauma") {
                            if ($scope.allDoctors[i].user_id == $scope.specialistProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Pathology" && $scope.selectedSpecialty == "Pathology") {
                            if ($scope.allDoctors[i].user_id == $scope.specialistProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Pediatric" && $scope.selectedSpecialty == "Pediatric") {
                            if ($scope.allDoctors[i].user_id == $scope.specialistProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Physiotherapy" && $scope.selectedSpecialty == "Physiotherapy") {
                            if ($scope.allDoctors[i].user_id == $scope.specialistProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Psychiatric" && $scope.selectedSpecialty == "Psychiatric") {
                            if ($scope.allDoctors[i].user_id == $scope.specialistProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Surgery" && $scope.selectedSpecialty == "Surgery") {
                            if ($scope.allDoctors[i].user_id == $scope.specialistProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                    }
                }
            }
            else if ($scope.selectedSpecialty && $scope.resident == true) {
                for (var i = 0; i < $scope.allDoctors.length; i++) {
                    for (var j = 0; j < $scope.residentProviders.length; j++) {
                        if ($scope.allDoctors[i].role == "Radiology" && $scope.selectedSpecialty == "Radiology") {
                            if ($scope.allDoctors[i].user_id == $scope.residentProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Dentistry" && $scope.selectedSpecialty == "Dentistry") {
                            if ($scope.allDoctors[i].user_id == $scope.residentProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Anesthesiology" && $scope.selectedSpecialty == "Anesthesiology") {
                            if ($scope.allDoctors[i].user_id == $scope.residentProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Dermatovenerology" && $scope.selectedSpecialty == "Dermatovenerology") {
                            if ($scope.allDoctors[i].user_id == $scope.residentProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "EMCC" && $scope.selectedSpecialty == "EMCC") {
                            if ($scope.allDoctors[i].user_id == $scope.residentProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "ENT" && $scope.selectedSpecialty == "ENT") {
                            if ($scope.allDoctors[i].user_id == $scope.residentProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Internal Medicine" && $scope.selectedSpecialty == "Internal Medicine") {
                            if ($scope.allDoctors[i].user_id == $scope.residentProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Neurology" && $scope.selectedSpecialty == "Neurology") {
                            if ($scope.allDoctors[i].user_id == $scope.residentProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "OBGYN" && $scope.selectedSpecialty == "OBGYN") {
                            if ($scope.allDoctors[i].user_id == $scope.residentProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Occupational Therapy" && $scope.selectedSpecialty == "Occupational Therapy") {
                            if ($scope.allDoctors[i].user_id == $scope.residentProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "OMF Surgery" && $scope.selectedSpecialty == "OMF Surgery") {
                            if ($scope.allDoctors[i].user_id == $scope.residentProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Ophthalmology" && $scope.selectedSpecialty == "Ophthalmology") {
                            if ($scope.allDoctors[i].user_id == $scope.residentProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Optometry" && $scope.selectedSpecialty == "Optometry") {
                            if ($scope.allDoctors[i].user_id == $scope.residentProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Orthopedic & Trauma" && $scope.selectedSpecialty == "Orthopedic & Trauma") {
                            if ($scope.allDoctors[i].user_id == $scope.residentProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Pathology" && $scope.selectedSpecialty == "Pathology") {
                            if ($scope.allDoctors[i].user_id == $scope.residentProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Pediatric" && $scope.selectedSpecialty == "Pediatric") {
                            if ($scope.allDoctors[i].user_id == $scope.residentProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Physiotherapy" && $scope.selectedSpecialty == "Physiotherapy") {
                            if ($scope.allDoctors[i].user_id == $scope.residentProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Psychiatric" && $scope.selectedSpecialty == "Psychiatric") {
                            if ($scope.allDoctors[i].user_id == $scope.residentProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                        else if ($scope.allDoctors[i].role == "Surgery" && $scope.selectedSpecialty == "Surgery") {
                            if ($scope.allDoctors[i].user_id == $scope.residentProviders[j].user_id) {
                                $scope.doctors.push($scope.allDoctors[i]);
                                $scope.currentDoctors = $scope.doctors;
                            }
                        }
                    }
                }
            }
        }
        var defaultSpecialities = [
            "Anesthesiology", "Dentistry", "Dermatovenerology", "EMCC", "ENT",
            "Internal Medicine", "Neurology", "OBGYN", "Occupational Therapy",
            "OMF Surgery", "Ophthalmology", "Optometry", "Orthopedic & Trauma",
            "Pathology", "Pediatric", "Physiotherapy", "Psychiatric", "Radiology", "Surgery"
        ];
        $scope.specialities = defaultSpecialities;

        var getReferalHospitalAndDurationUniteConcepts = function () {
            return dispositionService.getDurationUniteConcept().then(function (response) {
                if (response.data.results.length > 0 && response.data.results[0].answers.length > 0) {
                    $scope.durationUniteConcepts = response.data.results[0].answers.map((e) => e.name.name);
                } else {
                    $scope.durationUniteConcepts = ['Hour', 'Day'];
                }
            }).catch(function () {
                $scope.durationUniteConcepts = ['Hour', 'Day'];
            });
        };
        getReferalHospitalAndDurationUniteConcepts();

        var visitType = visitService.getVisitType();

        visitType.then(function (data) {
            const exist= $scope.patient.person;
            if (exist && $scope.patient.person.age <= 18 && $scope.patient.person.gender === 'M') {
                $scope.visitType = data.data.results
                    .filter(e => !$scope.femaleVisitTypeNames.includes(e.display));
            } else if (exist && $scope.patient.person.age > 18 && $scope.patient.person.gender === 'M') {
                $scope.visitType = data.data.results
                    .filter(e => !$scope.femaleVisitTypeNames.includes(e.display) && !$scope.pediVisitTypeNames.includes(e.display));
            } else if (exist && $scope.patient.person.age > 18 && $scope.patient.person.gender === 'F') {
                $scope.visitType = data.data.results
                    .filter(e => !$scope.pediVisitTypeNames.includes(e.display));
            } else {
                $scope.visitType = data.data.results;
            }
        })

        var getLinkageUuid = function () {
            var params = {
                q: "bahmni.sqlGet.linkageUuid"
            };
            return $http.get('/openmrs/ws/rest/v1/bahmnicore/sql', {
                method: "GET",
                params: params,
                withCredentials: true
            });
        };

        var getLinkageLocationUuid = function (vt_name) {
            var params = {
                q: "emrapi.getCorrespondigLocationId",
                vt_name: vt_name
            };
            return $http.get('/openmrs/ws/rest/v1/bahmnicore/sql', {
                method: "GET",
                params: params,
                withCredentials: true
            });
        };

        $scope.link = function (selectedVisitType) {
            var selectedVisit = _.filter($scope.visitType, function (vt) {
                return vt.display === selectedVisitType;
            });

            if (selectedVisit.length > 0) {
                let visitLocationUuid;
                getLinkageLocationUuid(selectedVisit[0].display).then(function (response) {
                    visitLocationUuid = response.data[0].uuid;
                    getLinkageUuid().then(function (r) {
                        getAllActiveVisits($scope.patient.uuid).then(function (visits) {
                            if (visits && visits.length > 0) {
                                visits.forEach(visit => {
                                    visitService.endVisit(visit.uuid);
                                    messagingService.showMessage('info', 'Patient current visit is closed successfully.');
                                });
                            }
                            if ($scope.$parent.activeVisit) {
                                visitService.endVisit($scope.$parent.activeVisit.uuid);
                            }
                            var intendedVisitDetail = { patient: $scope.patient.uuid, visitType: selectedVisit[0].uuid, location: visitLocationUuid, attributes: [{ value: selectedVisit[0].uuid, attributeType: r.data[0].uuid }] };
                            visitService.createVisit(intendedVisitDetail)
                            messagingService.showMessage('info', 'patient linkage is completed successfully.');
                        });
                    })
                })

            }
            else {
                messagingService.showMessage('info', 'patient linkage is not successed.');
            }

        }

        var getAllActiveVisits = async function (patient_uuid) {
            var params = new URLSearchParams({
                q: "emrapi.getAllActiveVisits",
                patient_uuid: patient_uuid
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
                return data;
            } catch (error) {
                console.error('Error fetching patient admission data:', error);
                throw error;
            }
        };

        $scope.closeVisit = function () {
            getAllActiveVisits($scope.patient.uuid).then(function(visits) {
                if (visits && visits.length > 0) {
                    visits.forEach(visit => {
                        visitService.endVisit(visit.uuid);
                        messagingService.showMessage('info', 'Patient current visit is closed successfully.');      
                    });
                }
            });
        };

        $scope.uncheckExceptSpecialist = function (specialist) {
            if (specialist) {
                $scope.senior = false;
                $scope.resident = false;
                $scope.gp = false;
                $scope.specialist = true;
            };
            suggestedProviders();
            getSpecialty();
        };
        $scope.uncheckExceptResident = function (resident) {
            if (resident) {
                $scope.specialist = false;
                $scope.senior = false;
                $scope.gp = false;
                $scope.intern = false;
            };
            suggestedProviders();
            getSpecialty();
        };
        $scope.providerLinkage = function (physicians) {
            if (physicians) {
                $scope.opds = false;
                $scope.linkageVisitType.value = ""
            };
        };
        $scope.opdLinkage = function (opds) {
            if (opds) {
                $scope.physicians = false;
                $scope.specialty.value = "";
                $scope.suggestedProvider.value = "";
                $scope.specialist = false;
                $scope.resident = false;
            };
        };
        $scope.showDispositionTypeInfo = function () {
            $scope.dispositionTypeInfo = !$scope.dispositionTypeInfo;
        };

        var getPreviousDispositionNote = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.dispositionNoteConceptUuid;
                });
            }
        };

        var getPreviousRefers = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.refersConceptUuid;
                });
            }
        };

        var getPreviousDurationOfStay = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.durationOfStayConceptUuid;
                });
            }
        };

        var getPreviousDurationOfStayUnite = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.durationOfStayUniteConceptUuid;
                });
            }
        };

        var getPreviousAdmissionWard = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.admissionWardConceptUuid;
                });
            }
        };


        var getPreviousLinkageVisitType = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.linkageVisitTypeConceptUuid;
                });
            }
        };

        var getPreviousSignature = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.signatureConceptUuid;
                });
            }
        };

        var getPreviousSpecialty = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.specialtyConceptUuid;
                });
            }
        };

        var getPreviousSuggestedProvider = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.suggestedProviderConceptUuid;
                });
            }
        };

        var getPreviousReasonForReferral = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.reasonForReferralConceptUuid;
                });
            }
        };

        var getPreviousClinicalHistory = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.clinicalHistoryConceptUuid;
                });
            }
        };

        var getPreviousTreatmentProvided = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.treatmentProvidedConceptUuid;
                });
            }
        };

        var getDispositionNotes = function () {
            var previousDispositionNotes = getPreviousDispositionNote();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(previousDispositionNotes) || { concept: { uuid: $scope.dispositionNoteConceptUuid } };
            }
            else {
                return { concept: { uuid: $scope.dispositionNoteConceptUuid } };
            }
        };

        var getRefers = function () {
            var previousRefers = getPreviousRefers();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(previousRefers) || { concept: { uuid: $scope.refersConceptUuid } };
            }
            else {
                return { concept: { uuid: $scope.refersConceptUuid } };
            }
        };

        var getReasonForReferral = function () {
            var previousReasonForReferral = getPreviousReasonForReferral();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(previousReasonForReferral) || { concept: { uuid: $scope.reasonForReferralConceptUuid } };
            }
            else {
                return { concept: { uuid: $scope.reasonForReferralConceptUuid } };
            }
        };

        var getClinicalHistory = function () {
            var previousClinicalHistory = getPreviousClinicalHistory();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(previousClinicalHistory) || { concept: { uuid: $scope.clinicalHistoryConceptUuid } };
            }
            else {
                return { concept: { uuid: $scope.clinicalHistoryConceptUuid } };
            }
        };

        var getTreatmentProvided = function () {
            var previousTreatmentProvided = getPreviousTreatmentProvided();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(previousTreatmentProvided) || { concept: { uuid: $scope.treatmentProvidedConceptUuid } };
            }
            else {
                return { concept: { uuid: $scope.treatmentProvidedConceptUuid } };
            }
        };

        var getPreviousReferralDepartment = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.referralDepartmentConceptUuid;
                });
            }
        };
        var getReferralDepartment = function () {
            var prev = getPreviousReferralDepartment();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(prev) || { concept: { uuid: $scope.referralDepartmentConceptUuid } };
            }
            return { concept: { uuid: $scope.referralDepartmentConceptUuid } };
        };

        var getPreviousPatientCondition = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.patientConditionConceptUuid;
                });
            }
        };
        var getPatientCondition = function () {
            var prev = getPreviousPatientCondition();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(prev) || { concept: { uuid: $scope.patientConditionConceptUuid } };
            }
            return { concept: { uuid: $scope.patientConditionConceptUuid } };
        };

        var getPreviousChiefComplaint = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.chiefComplaintConceptUuid;
                });
            }
        };
        var getChiefComplaint = function () {
            var prev = getPreviousChiefComplaint();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(prev) || { concept: { uuid: $scope.chiefComplaintConceptUuid } };
            }
            return { concept: { uuid: $scope.chiefComplaintConceptUuid } };
        };

        var getPreviousHistoryOfPresentIllness = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.historyOfPresentIllnessConceptUuid;
                });
            }
        };
        var getHistoryOfPresentIllness = function () {
            var prev = getPreviousHistoryOfPresentIllness();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(prev) || { concept: { uuid: $scope.historyOfPresentIllnessConceptUuid } };
            }
            return { concept: { uuid: $scope.historyOfPresentIllnessConceptUuid } };
        };

        var getPreviousSystolicBP = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.systolicBPConceptUuid;
                });
            }
        };
        var getSystolicBP = function () {
            var prev = getPreviousSystolicBP();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(prev) || { concept: { uuid: $scope.systolicBPConceptUuid } };
            }
            return { concept: { uuid: $scope.systolicBPConceptUuid } };
        };

        var getPreviousDiastolicBP = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.diastolicBPConceptUuid;
                });
            }
        };
        var getDiastolicBP = function () {
            var prev = getPreviousDiastolicBP();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(prev) || { concept: { uuid: $scope.diastolicBPConceptUuid } };
            }
            return { concept: { uuid: $scope.diastolicBPConceptUuid } };
        };

        var getPreviousPulseRate = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.pulseRateConceptUuid;
                });
            }
        };
        var getPulseRate = function () {
            var prev = getPreviousPulseRate();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(prev) || { concept: { uuid: $scope.pulseRateConceptUuid } };
            }
            return { concept: { uuid: $scope.pulseRateConceptUuid } };
        };

        var getPreviousRespiratoryRate = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.respiratoryRateConceptUuid;
                });
            }
        };
        var getRespiratoryRate = function () {
            var prev = getPreviousRespiratoryRate();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(prev) || { concept: { uuid: $scope.respiratoryRateConceptUuid } };
            }
            return { concept: { uuid: $scope.respiratoryRateConceptUuid } };
        };

        var getPreviousBodyTemperature = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.bodyTemperatureConceptUuid;
                });
            }
        };
        var getBodyTemperature = function () {
            var prev = getPreviousBodyTemperature();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(prev) || { concept: { uuid: $scope.bodyTemperatureConceptUuid } };
            }
            return { concept: { uuid: $scope.bodyTemperatureConceptUuid } };
        };

        var getPreviousOxygenSaturation = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.oxygenSaturationConceptUuid;
                });
            }
        };
        var getOxygenSaturation = function () {
            var prev = getPreviousOxygenSaturation();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(prev) || { concept: { uuid: $scope.oxygenSaturationConceptUuid } };
            }
            return { concept: { uuid: $scope.oxygenSaturationConceptUuid } };
        };

        var getPreviousOnOxygen = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.onOxygenConceptUuid;
                });
            }
        };
        var getOnOxygen = function () {
            var prev = getPreviousOnOxygen();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(prev) || { concept: { uuid: $scope.onOxygenConceptUuid } };
            }
            return { concept: { uuid: $scope.onOxygenConceptUuid } };
        };

        var getPreviousLabResult = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.labResultConceptUuid;
                });
            }
        };
        var getLabResult = function () {
            var prev = getPreviousLabResult();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(prev) || { concept: { uuid: $scope.labResultConceptUuid } };
            }
            return { concept: { uuid: $scope.labResultConceptUuid } };
        };

        var getPreviousReferralDiagnosis = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.referralDiagnosisConceptUuid;
                });
            }
        };
        var getReferralDiagnosis = function () {
            var prev = getPreviousReferralDiagnosis();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(prev) || { concept: { uuid: $scope.referralDiagnosisConceptUuid } };
            }
            return { concept: { uuid: $scope.referralDiagnosisConceptUuid } };
        };

        var getPreviousNeedAmbulance = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.needAmbulanceConceptUuid;
                });
            }
        };
        var getNeedAmbulance = function () {
            var prev = getPreviousNeedAmbulance();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(prev) || { concept: { uuid: $scope.needAmbulanceConceptUuid } };
            }
            return { concept: { uuid: $scope.needAmbulanceConceptUuid } };
        };

        var getPreviousNeedEscorting = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.needEscortingConceptUuid;
                });
            }
        };
        var getNeedEscorting = function () {
            var prev = getPreviousNeedEscorting();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(prev) || { concept: { uuid: $scope.needEscortingConceptUuid } };
            }
            return { concept: { uuid: $scope.needEscortingConceptUuid } };
        };

        var getPreviousReferralApprovedBy = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.referralApprovedByConceptUuid;
                });
            }
        };
        var getReferralApprovedBy = function () {
            var prev = getPreviousReferralApprovedBy();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(prev) || { concept: { uuid: $scope.referralApprovedByConceptUuid } };
            }
            return { concept: { uuid: $scope.referralApprovedByConceptUuid } };
        };

        var getPreviousReferralSeniorPhysicianSpecialty = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.referralSeniorPhysicianSpecialtyConceptUuid;
                });
            }
        };
        var getReferralSeniorPhysicianSpecialty = function () {
            var prev = getPreviousReferralSeniorPhysicianSpecialty();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(prev) || { concept: { uuid: $scope.referralSeniorPhysicianSpecialtyConceptUuid } };
            }
            return { concept: { uuid: $scope.referralSeniorPhysicianSpecialtyConceptUuid } };
        };

        var getPreviousReferralApprovalMethod = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.referralApprovalMethodConceptUuid;
                });
            }
        };
        var getReferralApprovalMethod = function () {
            var prev = getPreviousReferralApprovalMethod();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(prev) || { concept: { uuid: $scope.referralApprovalMethodConceptUuid } };
            }
            return { concept: { uuid: $scope.referralApprovalMethodConceptUuid } };
        };

        var getPreviousReferralApprovalDateTime = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.referralApprovalDateTimeConceptUuid;
                });
            }
        };
        var getReferralApprovalDateTime = function () {
            var prev = getPreviousReferralApprovalDateTime();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(prev) || { concept: { uuid: $scope.referralApprovalDateTimeConceptUuid } };
            }
            return { concept: { uuid: $scope.referralApprovalDateTimeConceptUuid } };
        };

        var getPreviousReferralApprovalNotes = function () {
            if (consultation.disposition && (!consultation.disposition.voided)) {
                return _.find(consultation.disposition.additionalObs, function (obs) {
                    return obs.concept.uuid === $scope.referralApprovalNotesConceptUuid;
                });
            }
        };
        var getReferralApprovalNotes = function () {
            var prev = getPreviousReferralApprovalNotes();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(prev) || { concept: { uuid: $scope.referralApprovalNotesConceptUuid } };
            }
            return { concept: { uuid: $scope.referralApprovalNotesConceptUuid } };
        };

        $scope.seniorPhysiciansList = [];
        var buildSeniorPhysiciansList = function () {
            if (!$scope.allDoctors || $scope.allDoctors.length === 0) return;
            var list = [];
            var seen = {};
            for (var i = 0; i < $scope.allDoctors.length; i++) {
                var doc = $scope.allDoctors[i];
                var fn = doc.FullName || (doc.person && doc.person.display) || doc.name || '';
                if (fn && !seen[fn.toLowerCase()]) {
                    seen[fn.toLowerCase()] = true;
                    list.push({
                        fullName: fn,
                        specialty: doc.role || 'Senior Physician'
                    });
                }
            }
            $scope.seniorPhysiciansList = list;
        };

        $scope.onSeniorPhysicianSelected = function () {
            if (!$scope.referralApprovedBy || !$scope.referralApprovedBy.value) return;
            var valLower = $scope.referralApprovedBy.value.trim().toLowerCase();
            for (var i = 0; i < $scope.seniorPhysiciansList.length; i++) {
                if ($scope.seniorPhysiciansList[i].fullName.toLowerCase() === valLower) {
                    if ((!$scope.referralSeniorPhysicianSpecialty || !$scope.referralSeniorPhysicianSpecialty.value) &&
                        $scope.seniorPhysiciansList[i].specialty && $scope.seniorPhysiciansList[i].specialty !== 'Senior Physician') {
                        $scope.referralSeniorPhysicianSpecialty.value = $scope.seniorPhysiciansList[i].specialty;
                    }
                    break;
                }
            }
        };

        var toEthiopianDateTime = function (d) {
            if (!d) return '';
            var gy = d.getFullYear();
            var gm = d.getMonth() + 1;
            var gd = d.getDate();
            var monthDays = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
            var isGregLeap = (gy % 4 === 0 && gy % 100 !== 0) || gy % 400 === 0;
            if (isGregLeap) monthDays[1] = 29;
            var ethNewYearDay = isGregLeap ? 12 : 11;
            var ethYear, daysSinceNewYear;
            if (gm > 9 || (gm === 9 && gd >= ethNewYearDay)) {
                ethYear = gy - 7;
                if (gm === 9) {
                    daysSinceNewYear = gd - ethNewYearDay;
                } else {
                    daysSinceNewYear = 30 - ethNewYearDay;
                    for (var i = 9; i < gm - 1; i++) {
                        daysSinceNewYear += monthDays[i];
                    }
                    daysSinceNewYear += gd;
                }
            } else {
                ethYear = gy - 8;
                var prevIsLeap = ((gy - 1) % 4 === 0 && (gy - 1) % 100 !== 0) || (gy - 1) % 400 === 0;
                var prevEthNewYearDay = prevIsLeap ? 12 : 11;
                daysSinceNewYear = 30 - prevEthNewYearDay + 92;
                var dayOfYear = 0;
                for (var j = 0; j < gm - 1; j++) {
                    dayOfYear += monthDays[j];
                }
                dayOfYear += gd;
                daysSinceNewYear += dayOfYear;
            }
            var ethMonth = Math.floor(daysSinceNewYear / 30) + 1;
            var ethDay = (daysSinceNewYear % 30) + 1;
            if (ethMonth > 13) ethMonth = 13;
            var ddStr = ('0' + ethDay).slice(-2);
            var mmStr = ('0' + ethMonth).slice(-2);
            var hh = ('0' + d.getHours()).slice(-2);
            var min = ('0' + d.getMinutes()).slice(-2);
            return ddStr + '/' + mmStr + '/' + ethYear + ' ' + hh + ':' + min;
        };

        $scope.updateApprovalDateTimeString = function () {
            if ($scope.referralApprovalDateTimeRaw) {
                var d = new Date($scope.referralApprovalDateTimeRaw);
                if (!isNaN(d.getTime())) {
                    var pad = function (n) { return (n < 10 ? '0' : '') + n; };
                    var str = d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()) + ' ' +
                              pad(d.getHours()) + ':' + pad(d.getMinutes()) + ':' + pad(d.getSeconds());
                    if ($scope.referralApprovalDateTime) {
                        $scope.referralApprovalDateTime.value = str;
                    }
                    $scope.ethiopianApprovalDateDisplay = toEthiopianDateTime(d);
                } else {
                    $scope.ethiopianApprovalDateDisplay = '';
                }
            } else {
                $scope.ethiopianApprovalDateDisplay = '';
            }
        };

        var getDurationOfStay = function () {
            var previousDurationOfStay = getPreviousDurationOfStay();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(previousDurationOfStay) || { concept: { uuid: $scope.durationOfStayConceptUuid } };
            }
            else {
                return { concept: { uuid: $scope.durationOfStayConceptUuid } };
            }
        };

        var getDurationOfStayUnite = function () {
            var previousDurationOfStayUnite = getPreviousDurationOfStayUnite();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(previousDurationOfStayUnite) || { concept: { uuid: $scope.durationOfStayUniteConceptUuid } };
            }
            else {
                return { concept: { uuid: $scope.durationOfStayUniteConceptUuid } };
            }
        };

        var getAdmissionWard = function () {
            var previousAdmissionWard = getPreviousAdmissionWard();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(previousAdmissionWard) || { concept: { uuid: $scope.admissionWardConceptUuid } };
            }
            else {
                return { concept: { uuid: $scope.admissionWardConceptUuid } };
            }
        };

        var getLinkageVisitType = function () {
            var previousLinkageVisitType = getPreviousLinkageVisitType();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(previousLinkageVisitType) || { concept: { uuid: $scope.linkageVisitTypeConceptUuid } };
            }
            else {
                return { concept: { uuid: $scope.linkageVisitTypeConceptUuid } };
            }
        };

        var getSignature = function () {
            var previousSignature = getPreviousSignature();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(previousSignature) || { concept: { uuid: $scope.signatureConceptUuid } };
            }
            else {
                return { concept: { uuid: $scope.signatureConceptUuid } };
            }
        };

        var getSpecialty = function () {
            var previousSpecialty = getPreviousSpecialty();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(previousSpecialty) || { concept: { uuid: $scope.specialtyConceptUuid } };
            }
            else {
                return { concept: { uuid: $scope.specialtyConceptUuid } };
            }
        };

        var getSuggestedProvider = function () {
            var previousSuggestedProvider = getPreviousSuggestedProvider();
            if (getSelectedConceptName($scope.dispositionCode, $scope.dispositionActions)) {
                return _.cloneDeep(previousSuggestedProvider) || { concept: { uuid: $scope.suggestedProviderConceptUuid } };
            }
            else {
                return { concept: { uuid: $scope.suggestedProviderConceptUuid } };
            }
        };

        var linkageVisitTypes = function () {
            $scope.linkageVisitType = getLinkageVisitType();
            if ($scope.linkageVisitType.value) {
                $scope.opds = true;
                $scope.opdLinkage();
            }
        }

        var suggestedProviders = function () {
            $scope.suggestedProvider = getSuggestedProvider();
            var user_id = $scope.suggestedProvider?.value;
            switch (true) {
                case $scope.specialist:
                    $scope.suggestedProvider.value = $scope.currentDoctors?.find((provider) => provider.user_id == user_id);
                    break;
                case $scope.resident:
                    $scope.suggestedProvider.value = $scope.currentDoctors?.find((provider) => provider.user_id == user_id);
                    break;
            }
            if ($scope.suggestedProvider.value) {
                $scope.currentDoctors = $scope.allDoctors;
                for (var i = 0; i < $scope.currentDoctors.length; i++) {
                    for (var j = 0; j < $scope.specialistProviders.length; j++) {
                        // if ($scope.currentDoctors[i].user_id==$scope.specialistProviders[j].user_id) {
                        // $scope.specialist = true
                        // }

                        if ($scope.suggestedProvider.value == $scope.currentDoctors[i].user_id && $scope.currentDoctors[i].user_id == $scope.specialistProviders[j].user_id) {
                            $scope.specialist = true
                            $scope.physicians = true
                            $scope.providerLinkage();
                            $scope.uncheckExceptSpecialist();
                        }
                    }
                }
                for (var i = 0; i < $scope.currentDoctors.length; i++) {
                    for (var j = 0; j < $scope.residentProviders.length; j++) {
                        // if ($scope.currentDoctors[i].user_id==$scope.residentProviders[j].user_id) {
                        //     $scope.resident = true
                        // }

                        if ($scope.suggestedProvider.value == $scope.currentDoctors[i].user_id && $scope.currentDoctors[i].user_id == $scope.residentProviders[j].user_id) {
                            $scope.resident = true
                            $scope.physicians = true
                            $scope.providerLinkage();
                            $scope.uncheckExceptResident();
                        }
                    }
                }
            }


        }
        var getDispositionActionsPromise = function () {
            return dispositionService.getDispositionActions().then(function (response) {
                allDispositions = new Bahmni.Clinical.DispostionActionMapper().map(response.data.results[0].answers);
                $scope.dispositionActions = filterDispositionActions(allDispositions, $scope.$parent.visitSummary);
                $scope.dispositionCode = consultation.disposition && (!consultation.disposition.voided) ? consultation.disposition.code : null;
                $scope.dispositionNote = getDispositionNotes();
                $scope.refers = getRefers();
                $scope.durationOfStay = getDurationOfStay();
                $scope.durationOfStayUnite = getDurationOfStayUnite();
                $scope.admissionWard = getAdmissionWard();
                linkageVisitTypes();
                $scope.signature = getSignature();
                $scope.specialty = getSpecialty();
                $scope.reasonForReferral = getReasonForReferral();
                $scope.clinicalHistory = getClinicalHistory();
                $scope.treatmentProvided = getTreatmentProvided();
                $scope.referralDepartment = getReferralDepartment();
                $scope.patientCondition = getPatientCondition();
                $scope.chiefComplaint = getChiefComplaint();
                $scope.historyOfPresentIllness = getHistoryOfPresentIllness();
                $scope.systolicBP = getSystolicBP();
                $scope.diastolicBP = getDiastolicBP();
                $scope.pulseRate = getPulseRate();
                $scope.respiratoryRate = getRespiratoryRate();
                $scope.bodyTemperature = getBodyTemperature();
                $scope.oxygenSaturation = getOxygenSaturation();
                $scope.onOxygen = getOnOxygen();
                $scope.labResult = getLabResult();
                $scope.referralDiagnosis = getReferralDiagnosis();
                $scope.needAmbulance = getNeedAmbulance();
                $scope.needEscorting = getNeedEscorting();
                $scope.referralApprovedBy = getReferralApprovedBy();
                $scope.referralSeniorPhysicianSpecialty = getReferralSeniorPhysicianSpecialty();
                $scope.referralApprovalMethod = getReferralApprovalMethod();
                $scope.referralApprovalDateTime = getReferralApprovalDateTime();
                $scope.referralApprovalNotes = getReferralApprovalNotes();
                if ($scope.referralApprovalDateTime && $scope.referralApprovalDateTime.value) {
                    var parsed = new Date($scope.referralApprovalDateTime.value);
                    if (!isNaN(parsed.getTime())) {
                        $scope.referralApprovalDateTimeRaw = parsed;
                    }
                } else {
                    $scope.referralApprovalDateTimeRaw = new Date();
                    $scope.updateApprovalDateTimeString();
                }
                buildSeniorPhysiciansList();
                suggestedProviders();
            });
        };

        var getDispositionActions = function (finalDispositionActions, dispositions, action) {
            var copyOfFinalDispositionActions = _.cloneDeep(finalDispositionActions);
            var dispositionPresent = _.find(dispositions, action);
            if (dispositionPresent) {
                copyOfFinalDispositionActions.push(dispositionPresent);
            }
            return copyOfFinalDispositionActions;
        };
        $scope.getTranslatedDisposition = function (dispositionName) {
            var translatedName = Bahmni.Common.Util.TranslationUtil.translateAttribute(dispositionName, Bahmni.Common.Constants.disposition, $translate);
            return translatedName;
        };
        var filterDispositionActions = function (dispositions, visitSummary) {
            var defaultDispositions = ["Undo Discharge", "Admit Patient", "Transfer Patient", "Discharge Patient", "Refer Patient", "Give Appointment", "Keep Patient", "Leaving Against Medical Advice and Service", "Link Patient", "Emergency keep"];
            var finalDispositionActions = _.filter(dispositions, function (disposition) {
                return defaultDispositions.indexOf(disposition.name) < 0;
            });
            var isVisitOpen = visitSummary ? _.isEmpty(visitSummary.stopDateTime) : false;
            if (visitSummary && visitSummary.isDischarged() && isVisitOpen) {
                finalDispositionActions = getDispositionActions(finalDispositionActions, dispositions, { name: defaultDispositions[0]});
            }
            else if (visitSummary && visitSummary.isAdmitted() && isVisitOpen) {
                finalDispositionActions = getDispositionActions(finalDispositionActions, dispositions, { name: defaultDispositions[2] });
                finalDispositionActions = getDispositionActions(finalDispositionActions, dispositions, { name: defaultDispositions[3] });
                finalDispositionActions = getDispositionActions(finalDispositionActions, dispositions, { name: defaultDispositions[4] });
                finalDispositionActions = getDispositionActions(finalDispositionActions, dispositions, { name: defaultDispositions[8] });
                finalDispositionActions = getDispositionActions(finalDispositionActions, dispositions, { name: defaultDispositions[9] });
                finalDispositionActions = getDispositionActions(finalDispositionActions, dispositions, { name: defaultDispositions[7] });
            }
            else {
                finalDispositionActions = getDispositionActions(finalDispositionActions, dispositions, { name: defaultDispositions[1] });
                finalDispositionActions = getDispositionActions(finalDispositionActions, dispositions, { name: defaultDispositions[4] });
                finalDispositionActions = getDispositionActions(finalDispositionActions, dispositions, { name: defaultDispositions[8] });
                finalDispositionActions = getDispositionActions(finalDispositionActions, dispositions, { name: defaultDispositions[5] });
                finalDispositionActions = getDispositionActions(finalDispositionActions, dispositions, { name: defaultDispositions[6] });
                finalDispositionActions = getDispositionActions(finalDispositionActions, dispositions, { name: defaultDispositions[9] });
                finalDispositionActions = getDispositionActions(finalDispositionActions, dispositions, { name: defaultDispositions[7] });
            }
            return finalDispositionActions;
        };

        $scope.isRetrospectiveMode = function () {
            return !_.isEmpty(retrospectiveEntryService.getRetrospectiveEntry());
        };

        $scope.showWarningForEarlierDispositionNote = function () {
            return !$scope.dispositionCode && consultation.disposition;
        };

        var getDispositionNotePromise = function () {
            $scope.referralDepartmentConceptUuid = 'a1b2c3d4-e5f6-7890-abcd-100000000001';
            $scope.patientConditionConceptUuid = 'a1b2c3d4-e5f6-7890-abcd-100000000002';
            $scope.needAmbulanceConceptUuid = 'a1b2c3d4-e5f6-7890-abcd-100000000003';
            $scope.needEscortingConceptUuid = 'a1b2c3d4-e5f6-7890-abcd-100000000004';
            $scope.referralApprovedByConceptUuid = 'a1b2c3d4-e5f6-7890-abcd-100000000005';
            $scope.referralSeniorPhysicianSpecialtyConceptUuid = 'a1b2c3d4-e5f6-7890-abcd-100000000006';
            $scope.referralApprovalMethodConceptUuid = 'a1b2c3d4-e5f6-7890-abcd-100000000007';
            $scope.referralApprovalDateTimeConceptUuid = 'a1b2c3d4-e5f6-7890-abcd-100000000008';
            $scope.referralApprovalNotesConceptUuid = 'a1b2c3d4-e5f6-7890-abcd-100000000009';
            $scope.chiefComplaintConceptUuid = '160531AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA';
            $scope.historyOfPresentIllnessConceptUuid = '1390AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA';
            $scope.systolicBPConceptUuid = '5085AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA';
            $scope.diastolicBPConceptUuid = '5086AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA';
            $scope.pulseRateConceptUuid = '5087AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA';
            $scope.respiratoryRateConceptUuid = '5242AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA';
            $scope.bodyTemperatureConceptUuid = '9bb0795c-4ff0-0305-1990-000000000020';
            $scope.oxygenSaturationConceptUuid = '5092AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA';
            $scope.onOxygenConceptUuid = '6212e416-d1bd-4126-b159-83845b59f3f0';
            $scope.labResultConceptUuid = '161577AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA';
            $scope.referralDiagnosisConceptUuid = 'd3681d2a-5e07-11ef-8f7c-0242ac120002';
            return $q.all([
                dispositionService.getDispositionNoteConcept().then(function (response) {
                    $scope.dispositionNoteConceptUuid = response.data.results[0].uuid;
                }),
                dispositionService.getRefersConcept().then(function (response) {
                    $scope.refersConceptUuid = response.data.results[0].uuid;
                }),
                dispositionService.getDurationOfStayConcept().then(function (response) {
                    $scope.durationOfStayConceptUuid = response.data.results[0].uuid;
                }),
                dispositionService.getDurationOfStayUniteConcept().then(function (response) {
                    $scope.durationOfStayUniteConceptUuid = response.data.results[0].uuid;
                }),
                dispositionService.getAdmissionWardConcept().then(function (response) {
                    $scope.admissionWardConceptUuid = response.data.results[0].uuid;
                }),
                dispositionService.getLinkageVisitTypeConcept().then(function (response) {
                    $scope.linkageVisitTypeConceptUuid = response.data.results[0].uuid;
                }),
                dispositionService.getSignatureConcept().then(function (response) {
                    $scope.signatureConceptUuid = response.data.results[0].uuid;
                }),
                dispositionService.getSpecialtyConcept().then(function (response) {
                    $scope.specialtyConceptUuid = response.data.results[0].uuid;
                }),
                dispositionService.getSuggestedProviderConcept().then(function (response) {
                    $scope.suggestedProviderConceptUuid = response.data.results[0].uuid;
                }),
                $http.get(Bahmni.Common.Constants.conceptSearchByFullNameUrl + "&name=Reason for referral (text)&v=custom:(uuid)").then(function (response) {
                    $scope.reasonForReferralConceptUuid = response.data.results[0] ? response.data.results[0].uuid : null;
                }),
                $http.get(Bahmni.Common.Constants.conceptSearchByFullNameUrl + "&name=Relevant clinical history&v=custom:(uuid)").then(function (response) {
                    $scope.clinicalHistoryConceptUuid = response.data.results[0] ? response.data.results[0].uuid : null;
                }),
                $http.get(Bahmni.Common.Constants.conceptSearchByFullNameUrl + "&name=Treatment provided&v=custom:(uuid)").then(function (response) {
                    $scope.treatmentProvidedConceptUuid = response.data.results[0] ? response.data.results[0].uuid : null;
                }),
                $http.get(Bahmni.Common.Constants.conceptSearchByFullNameUrl + "&name=Referral department&v=custom:(uuid)").then(function (response) {
                    if (response.data.results && response.data.results[0]) {
                        $scope.referralDepartmentConceptUuid = response.data.results[0].uuid;
                    }
                }),
                $http.get(Bahmni.Common.Constants.conceptSearchByFullNameUrl + "&name=Patient condition at referral&v=custom:(uuid)").then(function (response) {
                    if (response.data.results && response.data.results[0]) {
                        $scope.patientConditionConceptUuid = response.data.results[0].uuid;
                    }
                }),
                $http.get(Bahmni.Common.Constants.conceptSearchByFullNameUrl + "&name=Need ambulance&v=custom:(uuid)").then(function (response) {
                    if (response.data.results && response.data.results[0]) {
                        $scope.needAmbulanceConceptUuid = response.data.results[0].uuid;
                    }
                }),
                $http.get(Bahmni.Common.Constants.conceptSearchByFullNameUrl + "&name=Need escorting professionals&v=custom:(uuid)").then(function (response) {
                    if (response.data.results && response.data.results[0]) {
                        $scope.needEscortingConceptUuid = response.data.results[0].uuid;
                    }
                }),
                $http.get(Bahmni.Common.Constants.conceptSearchByFullNameUrl + "&name=Referral Approved By&v=custom:(uuid)").then(function (response) {
                    if (response.data.results && response.data.results[0]) {
                        $scope.referralApprovedByConceptUuid = response.data.results[0].uuid;
                    }
                }),
                $http.get(Bahmni.Common.Constants.conceptSearchByFullNameUrl + "&name=Referral Senior Physician Specialty&v=custom:(uuid)").then(function (response) {
                    if (response.data.results && response.data.results[0]) {
                        $scope.referralSeniorPhysicianSpecialtyConceptUuid = response.data.results[0].uuid;
                    }
                }),
                $http.get(Bahmni.Common.Constants.conceptSearchByFullNameUrl + "&name=Referral Approval Method&v=custom:(uuid)").then(function (response) {
                    if (response.data.results && response.data.results[0]) {
                        $scope.referralApprovalMethodConceptUuid = response.data.results[0].uuid;
                    }
                }),
                $http.get(Bahmni.Common.Constants.conceptSearchByFullNameUrl + "&name=Referral Approval DateTime&v=custom:(uuid)").then(function (response) {
                    if (response.data.results && response.data.results[0]) {
                        $scope.referralApprovalDateTimeConceptUuid = response.data.results[0].uuid;
                    }
                }),
                $http.get(Bahmni.Common.Constants.conceptSearchByFullNameUrl + "&name=Referral Approval Notes&v=custom:(uuid)").then(function (response) {
                    if (response.data.results && response.data.results[0]) {
                        $scope.referralApprovalNotesConceptUuid = response.data.results[0].uuid;
                    }
                })
            ]);
        };

        var loadDispositionActions = function () {
            return getDispositionNotePromise().then(getDispositionActionsPromise);
        };

        $scope.clearDispositionNote = function () {
            $scope.dispositionNote.value = null;
            $scope.refers.value = null;
            $scope.durationOfStay.value = null;
            $scope.durationOfStayUnite.value = null;
            $scope.admissionWard.value = null;
            $scope.linkageVisitType.value = null;
            $scope.signature.value = null;
            $scope.specialty.value = null;
            $scope.suggestedProvider.value = null;
            $scope.reasonForReferral.value = null;
            $scope.clinicalHistory.value = null;
            $scope.treatmentProvided.value = null;
            if ($scope.referralDepartment) $scope.referralDepartment.value = null;
            if ($scope.patientCondition) $scope.patientCondition.value = null;
            if ($scope.chiefComplaint) $scope.chiefComplaint.value = null;
            if ($scope.historyOfPresentIllness) $scope.historyOfPresentIllness.value = null;
            if ($scope.systolicBP) $scope.systolicBP.value = null;
            if ($scope.diastolicBP) $scope.diastolicBP.value = null;
            if ($scope.pulseRate) $scope.pulseRate.value = null;
            if ($scope.respiratoryRate) $scope.respiratoryRate.value = null;
            if ($scope.bodyTemperature) $scope.bodyTemperature.value = null;
            if ($scope.oxygenSaturation) $scope.oxygenSaturation.value = null;
            if ($scope.onOxygen) $scope.onOxygen.value = null;
            if ($scope.labResult) $scope.labResult.value = null;
            if ($scope.referralDiagnosis) $scope.referralDiagnosis.value = null;
            if ($scope.needAmbulance) $scope.needAmbulance.value = null;
            if ($scope.needEscorting) $scope.needEscorting.value = null;
            if ($scope.referralApprovedBy) $scope.referralApprovedBy.value = null;
            if ($scope.referralSeniorPhysicianSpecialty) $scope.referralSeniorPhysicianSpecialty.value = null;
            if ($scope.referralApprovalMethod) $scope.referralApprovalMethod.value = null;
            if ($scope.referralApprovalDateTime) $scope.referralApprovalDateTime.value = null;
            if ($scope.referralApprovalNotes) $scope.referralApprovalNotes.value = null;
            $scope.referralApprovalDateTimeRaw = null;
        };

        var getSelectedConceptName = function (dispositionCode, dispositions) {
            var selectedDispositionConceptName = _.findLast(dispositions, { code: dispositionCode }) || {};
            return selectedDispositionConceptName.name;
        };

        var booleanConceptUuids = [
            '6212e416-d1bd-4126-b159-83845b59f3f0'
        ];
        var convertObsValue = function (obs, conceptUuid) {
            var clone = _.clone(obs);
            if (clone.value === null || clone.value === undefined || clone.value === '') return clone;
            if (booleanConceptUuids.indexOf(conceptUuid) >= 0) {
                clone.value = (clone.value === true || clone.value === 'Yes' || clone.value === 'true') ? 'true' : 'false';
            } else {
                clone.value = String(clone.value);
            }
            return clone;
        };

        var getSelectedDisposition = function () {
            if ($scope.dispositionCode) {
                $scope.dispositionNote.voided = !$scope.dispositionNote.value;
                $scope.refers.voided = !$scope.refers.value;
                $scope.durationOfStay.voided = !$scope.durationOfStay.value;
                $scope.durationOfStayUnite.voided = !$scope.durationOfStayUnite.value;
                $scope.admissionWard.voided = !$scope.admissionWard.value;
                $scope.linkageVisitType.voided = !$scope.linkageVisitType.value;
                $scope.signature.voided = !$scope.signature.value;
                $scope.specialty.voided = !$scope.specialty.value;
                $scope.suggestedProvider.voided = !$scope.suggestedProvider.value;
                $scope.reasonForReferral.voided = !$scope.reasonForReferral.value;
                $scope.clinicalHistory.voided = !$scope.clinicalHistory.value;
                $scope.treatmentProvided.voided = !$scope.treatmentProvided.value;
                if ($scope.referralDepartment) $scope.referralDepartment.voided = !$scope.referralDepartment.value;
                if ($scope.patientCondition) $scope.patientCondition.voided = !$scope.patientCondition.value;
                if ($scope.chiefComplaint) $scope.chiefComplaint.voided = !$scope.chiefComplaint.value;
                if ($scope.historyOfPresentIllness) $scope.historyOfPresentIllness.voided = !$scope.historyOfPresentIllness.value;
                if ($scope.systolicBP) $scope.systolicBP.voided = !$scope.systolicBP.value;
                if ($scope.diastolicBP) $scope.diastolicBP.voided = !$scope.diastolicBP.value;
                if ($scope.pulseRate) $scope.pulseRate.voided = !$scope.pulseRate.value;
                if ($scope.respiratoryRate) $scope.respiratoryRate.voided = !$scope.respiratoryRate.value;
                if ($scope.bodyTemperature) $scope.bodyTemperature.voided = !$scope.bodyTemperature.value;
                if ($scope.oxygenSaturation) $scope.oxygenSaturation.voided = !$scope.oxygenSaturation.value;
                if ($scope.onOxygen) $scope.onOxygen.voided = !$scope.onOxygen.value;
                if ($scope.labResult) $scope.labResult.voided = !$scope.labResult.value;
                if ($scope.referralDiagnosis) $scope.referralDiagnosis.voided = !$scope.referralDiagnosis.value;
                if ($scope.needAmbulance) $scope.needAmbulance.voided = !$scope.needAmbulance.value;
                if ($scope.needEscorting) $scope.needEscorting.voided = !$scope.needEscorting.value;
                if ($scope.referralApprovedBy) $scope.referralApprovedBy.voided = !$scope.referralApprovedBy.value;
                if ($scope.referralSeniorPhysicianSpecialty) $scope.referralSeniorPhysicianSpecialty.voided = !$scope.referralSeniorPhysicianSpecialty.value;
                if ($scope.referralApprovalMethod) $scope.referralApprovalMethod.voided = !$scope.referralApprovalMethod.value;
                if ($scope.referralApprovalDateTime) $scope.referralApprovalDateTime.voided = !$scope.referralApprovalDateTime.value;
                if ($scope.referralApprovalNotes) $scope.referralApprovalNotes.voided = !$scope.referralApprovalNotes.value;
                var disposition = {
                    additionalObs: [], referObs: [], durationOfStayObs: [], durationOfStayUniteObs: [], admissionWardObs: [], linkageVisitTypeObs: [],
                    signatureObs: [], specialtyObs: [], suggestedProviderObs: [], dispositionNoteObs: [],
                    reasonForReferralObs: [], clinicalHistoryObs: [], treatmentProvidedObs: [],
                    referralDepartmentObs: [], patientConditionObs: [], chiefComplaintObs: [], historyOfPresentIllnessObs: [],
                    systolicBPObs: [], diastolicBPObs: [], pulseRateObs: [], respiratoryRateObs: [],
                    bodyTemperatureObs: [], oxygenSaturationObs: [], onOxygenObs: [],
                    labResultObs: [], referralDiagnosisObs: [], needAmbulanceObs: [], needEscortingObs: [],
                    referralApprovedByObs: [], referralSeniorPhysicianSpecialtyObs: [],
                    referralApprovalMethodObs: [], referralApprovalDateTimeObs: [], referralApprovalNotesObs: [],
                    dispositionDateTime: consultation.disposition && consultation.disposition.dispositionDateTime,
                    code: $scope.dispositionCode,
                    conceptName: getSelectedConceptName($scope.dispositionCode, allDispositions)
                };
                if ($scope.dispositionNote.value || $scope.dispositionNote.uuid || $scope.refers.value || $scope.refers.uuid || $scope.admissionWard.value || $scope.admissionWard.uuid || $scope.linkageVisitType.value || $scope.linkageVisitType.uuid || $scope.durationOfStay.value || $scope.durationOfStay.uuid || $scope.specialty.value || $scope.specialty.uuid || $scope.suggestedProvider.value || $scope.suggestedProvider.uuid || $scope.signature.value || $scope.signature.uuid || $scope.reasonForReferral.value || $scope.reasonForReferral.uuid || $scope.clinicalHistory.value || $scope.clinicalHistory.uuid || $scope.treatmentProvided.value || $scope.treatmentProvided.uuid || $scope.referralDepartment.value || $scope.referralDepartment.uuid || $scope.patientCondition.value || $scope.patientCondition.uuid || $scope.chiefComplaint.value || $scope.chiefComplaint.uuid || $scope.historyOfPresentIllness.value || $scope.historyOfPresentIllness.uuid || $scope.systolicBP.value || $scope.systolicBP.uuid || $scope.diastolicBP.value || $scope.diastolicBP.uuid || $scope.pulseRate.value || $scope.pulseRate.uuid || $scope.respiratoryRate.value || $scope.respiratoryRate.uuid || $scope.bodyTemperature.value || $scope.bodyTemperature.uuid || $scope.oxygenSaturation.value || $scope.oxygenSaturation.uuid || $scope.onOxygen.value || $scope.onOxygen.uuid || $scope.labResult.value || $scope.labResult.uuid || $scope.referralDiagnosis.value || $scope.referralDiagnosis.uuid || $scope.needAmbulance.value || $scope.needAmbulance.uuid || $scope.needEscorting.value || $scope.needEscorting.uuid || ($scope.referralApprovedBy && ($scope.referralApprovedBy.value || $scope.referralApprovedBy.uuid)) || ($scope.referralSeniorPhysicianSpecialty && ($scope.referralSeniorPhysicianSpecialty.value || $scope.referralSeniorPhysicianSpecialty.uuid)) || ($scope.referralApprovalMethod && ($scope.referralApprovalMethod.value || $scope.referralApprovalMethod.uuid)) || ($scope.referralApprovalDateTime && ($scope.referralApprovalDateTime.value || $scope.referralApprovalDateTime.uuid)) || ($scope.referralApprovalNotes && ($scope.referralApprovalNotes.value || $scope.referralApprovalNotes.uuid))) {
                    if ($scope.dispositionNote.value || $scope.dispositionNote.uuid) {
                        disposition.dispositionNoteObs = [_.clone($scope.dispositionNote)];
                    }
                    if ($scope.refers.value || $scope.refers.uuid) {
                        disposition.referObs = [_.clone($scope.refers)];
                    }
                    if ($scope.durationOfStay.value || $scope.durationOfStay.uuid) {
                        disposition.durationOfStayObs = [_.clone($scope.durationOfStay)];
                        disposition.durationOfStayUniteObs = [_.clone($scope.durationOfStayUnite)];
                    }
                    if ($scope.admissionWard.value || $scope.admissionWard.uuid) {
                        disposition.admissionWardObs = [_.clone($scope.admissionWard)];
                    }
                    if ($scope.linkageVisitType.value || $scope.linkageVisitType.uuid) {
                        disposition.linkageVisitTypeObs = [_.clone($scope.linkageVisitType)];
                    }
                    if ($scope.specialty.value || $scope.specialty.uuid) {
                        disposition.specialtyObs = [_.clone($scope.specialty)];
                    }
                    if ($scope.suggestedProvider.value) {
                        disposition.suggestedProviderObs = [_.clone($scope.suggestedProvider)];
                        disposition.suggestedProviderObs[0].value = disposition.suggestedProviderObs[0].value.user_id.toString();
                    }
                    if ($scope.signature.value || $scope.signature.uuid) {
                        disposition.signatureObs = [_.clone($scope.signature)];
                    }
                    if ($scope.reasonForReferral.value || $scope.reasonForReferral.uuid) {
                        disposition.reasonForReferralObs = [_.clone($scope.reasonForReferral)];
                    }
                    if ($scope.clinicalHistory.value || $scope.clinicalHistory.uuid) {
                        disposition.clinicalHistoryObs = [_.clone($scope.clinicalHistory)];
                    }
                    if ($scope.treatmentProvided.value || $scope.treatmentProvided.uuid) {
                        disposition.treatmentProvidedObs = [_.clone($scope.treatmentProvided)];
                    }
                    if ($scope.referralDepartment.value || $scope.referralDepartment.uuid) {
                        disposition.referralDepartmentObs = [_.clone($scope.referralDepartment)];
                    }
                    if ($scope.patientCondition.value || $scope.patientCondition.uuid) {
                        disposition.patientConditionObs = [_.clone($scope.patientCondition)];
                    }
                    if ($scope.chiefComplaint.value || $scope.chiefComplaint.uuid) {
                        disposition.chiefComplaintObs = [_.clone($scope.chiefComplaint)];
                    }
                    if ($scope.historyOfPresentIllness.value || $scope.historyOfPresentIllness.uuid) {
                        disposition.historyOfPresentIllnessObs = [_.clone($scope.historyOfPresentIllness)];
                    }
                    if ($scope.systolicBP.value || $scope.systolicBP.uuid) {
                        disposition.systolicBPObs = [convertObsValue($scope.systolicBP, $scope.systolicBPConceptUuid)];
                    }
                    if ($scope.diastolicBP.value || $scope.diastolicBP.uuid) {
                        disposition.diastolicBPObs = [convertObsValue($scope.diastolicBP, $scope.diastolicBPConceptUuid)];
                    }
                    if ($scope.pulseRate.value || $scope.pulseRate.uuid) {
                        disposition.pulseRateObs = [convertObsValue($scope.pulseRate, $scope.pulseRateConceptUuid)];
                    }
                    if ($scope.respiratoryRate.value || $scope.respiratoryRate.uuid) {
                        disposition.respiratoryRateObs = [convertObsValue($scope.respiratoryRate, $scope.respiratoryRateConceptUuid)];
                    }
                    if ($scope.bodyTemperature.value || $scope.bodyTemperature.uuid) {
                        disposition.bodyTemperatureObs = [convertObsValue($scope.bodyTemperature, $scope.bodyTemperatureConceptUuid)];
                    }
                    if ($scope.oxygenSaturation.value || $scope.oxygenSaturation.uuid) {
                        disposition.oxygenSaturationObs = [convertObsValue($scope.oxygenSaturation, $scope.oxygenSaturationConceptUuid)];
                    }
                    if ($scope.onOxygen.value || $scope.onOxygen.uuid) {
                        disposition.onOxygenObs = [convertObsValue($scope.onOxygen, $scope.onOxygenConceptUuid)];
                    }
                    if ($scope.labResult.value || $scope.labResult.uuid) {
                        disposition.labResultObs = [_.clone($scope.labResult)];
                    }
                    if ($scope.referralDiagnosis.value || $scope.referralDiagnosis.uuid) {
                        disposition.referralDiagnosisObs = [_.clone($scope.referralDiagnosis)];
                    }
                    if ($scope.needAmbulance.value || $scope.needAmbulance.uuid) {
                        disposition.needAmbulanceObs = [_.clone($scope.needAmbulance)];
                    }
                    if ($scope.needEscorting.value || $scope.needEscorting.uuid) {
                        disposition.needEscortingObs = [_.clone($scope.needEscorting)];
                    }
                    if ($scope.referralApprovedBy && ($scope.referralApprovedBy.value || $scope.referralApprovedBy.uuid)) {
                        disposition.referralApprovedByObs = [_.clone($scope.referralApprovedBy)];
                    }
                    if ($scope.referralSeniorPhysicianSpecialty && ($scope.referralSeniorPhysicianSpecialty.value || $scope.referralSeniorPhysicianSpecialty.uuid)) {
                        disposition.referralSeniorPhysicianSpecialtyObs = [_.clone($scope.referralSeniorPhysicianSpecialty)];
                    }
                    if ($scope.referralApprovalMethod && ($scope.referralApprovalMethod.value || $scope.referralApprovalMethod.uuid)) {
                        disposition.referralApprovalMethodObs = [_.clone($scope.referralApprovalMethod)];
                    }
                    if ($scope.referralApprovalDateTime && ($scope.referralApprovalDateTime.value || $scope.referralApprovalDateTime.uuid)) {
                        disposition.referralApprovalDateTimeObs = [_.clone($scope.referralApprovalDateTime)];
                    }
                    if ($scope.referralApprovalNotes && ($scope.referralApprovalNotes.value || $scope.referralApprovalNotes.uuid)) {
                        disposition.referralApprovalNotesObs = [_.clone($scope.referralApprovalNotes)];
                    }
                    disposition.additionalObs = [...disposition.referObs, ...disposition.dispositionNoteObs, ...disposition.durationOfStayObs, ...disposition.durationOfStayUniteObs, ...disposition.admissionWardObs, ...disposition.linkageVisitTypeObs, ...disposition.specialtyObs, ...disposition.suggestedProviderObs, ...disposition.signatureObs, ...disposition.reasonForReferralObs, ...disposition.clinicalHistoryObs, ...disposition.treatmentProvidedObs, ...disposition.referralDepartmentObs, ...disposition.patientConditionObs, ...disposition.chiefComplaintObs, ...disposition.historyOfPresentIllnessObs, ...disposition.systolicBPObs, ...disposition.diastolicBPObs, ...disposition.pulseRateObs, ...disposition.respiratoryRateObs, ...disposition.bodyTemperatureObs, ...disposition.oxygenSaturationObs, ...disposition.onOxygenObs, ...disposition.labResultObs, ...disposition.referralDiagnosisObs, ...disposition.needAmbulanceObs, ...disposition.needEscortingObs, ...disposition.referralApprovedByObs, ...disposition.referralSeniorPhysicianSpecialtyObs, ...disposition.referralApprovalMethodObs, ...disposition.referralApprovalDateTimeObs, ...disposition.referralApprovalNotesObs];
                }
                return disposition;
            }
        };

        spinner.forPromise(loadDispositionActions(), '#disposition');

        var saveDispositions = function () {
            var selectedDisposition = getSelectedDisposition();
            if (selectedDisposition) {
                consultation.disposition = selectedDisposition;
            } else {
                if (consultation.disposition) {
                    consultation.disposition.voided = true;
                    consultation.disposition.voidReason = "Cancelled during encounter";
                }
            }
        };

        $scope.consultation.preSaveHandler.register("dispositionSaveHandlerKey", saveDispositions);
        $scope.$on('$destroy', saveDispositions);
    }]);
