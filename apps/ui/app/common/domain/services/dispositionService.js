'use strict';

angular.module('bahmni.common.domain')
    .factory('dispositionService', ['$http', '$rootScope', function ($http, $rootScope) {
        var getDispositionActions = function () {
            return $http.get(Bahmni.Common.Constants.conceptSearchByFullNameUrl +
                "&name=" + Bahmni.Common.Constants.dispositionConcept +
                "&v=custom:(uuid,name,answers:(uuid,name,mappings))", {cache: true});
        };

        var getDispositionNoteConcept = function () {
            return $http.get(Bahmni.Common.Constants.conceptSearchByFullNameUrl +
                "&name=" + Bahmni.Common.Constants.dispositionNoteConcept +
                "&v=custom:(uuid,name:(name))", {cache: true});
        };
        var getReferralHospitalConcept = function () {
            return $http.get(Bahmni.Common.Constants.conceptSearchByFullNameUrl +
                "&name=" + Bahmni.Common.Constants.referralHospitalConcept +
                "&v=custom:(uuid,name,answers:(uuid,name,mappings))", {cache: true});
        };
        var getDurationUniteConcept = function () {
            return $http.get(Bahmni.Common.Constants.conceptSearchByFullNameUrl +
                "&name=" + Bahmni.Common.Constants.durationUniteConcept +
                "&v=custom:(uuid,name,answers:(uuid,name,mappings))", {cache: true});
        };
        var getRefersConcept = function () {
            return $http.get(Bahmni.Common.Constants.conceptSearchByFullNameUrl +
                "&name=" + Bahmni.Common.Constants.refersConcept +
                "&v=custom:(uuid,name,answers:(uuid,name,mappings))", {cache: true});
        };
        var getDurationOfStayConcept = function () {
            return $http.get(Bahmni.Common.Constants.conceptSearchByFullNameUrl +
                "&name=" + Bahmni.Common.Constants.durationOfStayConcept +
                "&v=custom:(uuid,name,answers:(uuid,name,mappings))", {cache: true});
        };
        var getDurationOfStayUniteConcept = function () {
            return $http.get(Bahmni.Common.Constants.conceptSearchByFullNameUrl +
                "&name=" + Bahmni.Common.Constants.durationOfStayUniteConcept +
                "&v=custom:(uuid,name,answers:(uuid,name,mappings))", {cache: true});
        };
        var getAdmissionWardConcept = function () {
            return $http.get(Bahmni.Common.Constants.conceptSearchByFullNameUrl +
                "&name=" + Bahmni.Common.Constants.admissionWardConcept +
                "&v=custom:(uuid,name,answers:(uuid,name,mappings))", {cache: true});
        };
        var getLinkageVisitTypeConcept = function () {
            return $http.get(Bahmni.Common.Constants.conceptSearchByFullNameUrl +
                "&name=" + Bahmni.Common.Constants.linkageVisitTypeConcept +
                "&v=custom:(uuid,name,answers:(uuid,name,mappings))", {cache: true});
        };
        var getSignatureConcept = function () {
            return $http.get(Bahmni.Common.Constants.conceptSearchByFullNameUrl +
                "&name=" + Bahmni.Common.Constants.signatureConcept +
                "&v=custom:(uuid,name,answers:(uuid,name,mappings))", {cache: true});
        };
        var getSpecialtyConcept = function () {
            return $http.get(Bahmni.Common.Constants.conceptSearchByFullNameUrl +
                "&name=" + Bahmni.Common.Constants.specialtyConcept +
                "&v=custom:(uuid,name,answers:(uuid,name,mappings))", {cache: true});
        };
        var getSuggestedProviderConcept = function () {
            return $http.get(Bahmni.Common.Constants.conceptSearchByFullNameUrl +
                "&name=" + Bahmni.Common.Constants.suggestedProviderConcept +
                "&v=custom:(uuid,name,answers:(uuid,name,mappings))", {cache: true});
        };

        var getDispositionByVisit = function (visitUuid) {
            var locale = ($rootScope.currentUser && $rootScope.currentUser.userProperties && $rootScope.currentUser.userProperties.defaultLocale) || 'en';
            return $http.get(Bahmni.Common.Constants.bahmniDispositionByVisitUrl, {
                params: {visitUuid: visitUuid,
                    locale: locale},
                ignoreErrors: true
            });
        };

        var getDispositionByPatient = function (patientUuid, numberOfVisits) {
            var locale = ($rootScope.currentUser && $rootScope.currentUser.userProperties && $rootScope.currentUser.userProperties.defaultLocale) || 'en';
            return $http.get(Bahmni.Common.Constants.bahmniDispositionByPatientUrl, {
                params: {
                    patientUuid: patientUuid,
                    numberOfVisits: numberOfVisits,
                    locale: locale
                },
                ignoreErrors: true
            });
        };

        return {
            getDispositionActions: getDispositionActions,
            getDispositionNoteConcept: getDispositionNoteConcept,
            getReferralHospitalConcept: getReferralHospitalConcept,
            getDurationUniteConcept: getDurationUniteConcept,
            getRefersConcept: getRefersConcept,
            getDurationOfStayConcept: getDurationOfStayConcept,
            getDurationOfStayUniteConcept: getDurationOfStayUniteConcept,
            getAdmissionWardConcept: getAdmissionWardConcept,
            getLinkageVisitTypeConcept: getLinkageVisitTypeConcept,
            getSignatureConcept: getSignatureConcept,
            getSpecialtyConcept: getSpecialtyConcept,
            getSuggestedProviderConcept: getSuggestedProviderConcept,
            getDispositionByVisit: getDispositionByVisit,
            getDispositionByPatient: getDispositionByPatient
        };
    }]);
