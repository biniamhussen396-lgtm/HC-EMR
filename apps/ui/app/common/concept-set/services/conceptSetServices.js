'use strict';

angular.module('bahmni.common.conceptSet')
    .factory('conceptSetService', ['$http', '$q', '$bahmniTranslate', function ($http, $q, $bahmniTranslate) {
        var getConcept = function (params, cache) {
            var locale = params['locale'] || $bahmniTranslate.use() || 'en';
            var queryParams = angular.copy(params);
            queryParams['locale'] = locale;
            return $http.get(Bahmni.Common.Constants.conceptSearchByFullNameUrl, {
                params: queryParams,
                cache: cache
            }).then(function (response) {
                if ((!response.data || !response.data.results || response.data.results.length === 0) && locale !== 'en') {
                    var fallbackParams = angular.copy(params);
                    fallbackParams['locale'] = 'en';
                    return $http.get(Bahmni.Common.Constants.conceptSearchByFullNameUrl, {
                        params: fallbackParams,
                        cache: cache
                    });
                }
                return response;
            });
        };

        var getComputedValue = function (encounterData) {
            var url = Bahmni.Common.Constants.encounterModifierUrl;
            return $http.post(url, encounterData, {
                withCredentials: true,
                headers: {"Accept": "application/json", "Content-Type": "application/json"}
            });
        };

        var getObsTemplatesForProgram = function (programUuid) {
            var url = Bahmni.Common.Constants.entityMappingUrl;
            return $http.get(url, {
                params: {
                    entityUuid: programUuid,
                    mappingType: 'program_obstemplate',
                    s: 'byEntityAndMappingType'
                }
            });
        };

        return {
            getConcept: getConcept,
            getComputedValue: getComputedValue,
            getObsTemplatesForProgram: getObsTemplatesForProgram
        };
    }]);

