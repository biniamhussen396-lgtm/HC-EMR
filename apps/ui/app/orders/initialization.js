'use strict';

angular.module('bahmni.orders')
.factory('initialization', ['$rootScope', '$q', 'appService', 'spinner', 'configurations', 'LogicAndConditionConfigsLoader', 'orderTypeService', 'locationService',
    function ($rootScope, $q, appService, spinner, configurations, LogicAndConditionConfigsLoader, orderTypeService, locationService) {
        var getConfigs = async function () {
            try {
                // Clear existing configurations from localStorage
                const configKeys = [
                    'configs', 'calculationwithFormulaConfigs', 'calculationwithoutFormulaConfigs',
                    'skipLogicConfigs', 'scheduleLogicConfig', 'validationConfig', 
                    'orderSelectorConfig', 'selfUpdatingFields', 'fieldsNeedPageRefresh', 'scoreBasedCalculation'
                ];
                configKeys.forEach(key => localStorage.removeItem(key));

                // Load and save configurations in localStorage
                $rootScope.configs = await LogicAndConditionConfigsLoader.loadActionsAndAnnotations();
                localStorage.setItem('configs', JSON.stringify($rootScope.configs));
                $rootScope.calculationwithFormulaConfigs = await LogicAndConditionConfigsLoader.loadCalculationWithFormulaConfigs();
                localStorage.setItem('calculationwithFormulaConfigs', JSON.stringify($rootScope.calculationwithFormulaConfigs));
                $rootScope.calculationwithoutFormulaConfigs = await LogicAndConditionConfigsLoader.loadCalculationWithoutFormulaConfigs();
                localStorage.setItem('calculationwithoutFormulaConfigs', JSON.stringify($rootScope.calculationwithoutFormulaConfigs));
                $rootScope.skipLogicConfigs = await LogicAndConditionConfigsLoader.loadSkipLogicConfigs();
                localStorage.setItem('skipLogicConfigs', JSON.stringify($rootScope.skipLogicConfigs));
                $rootScope.scheduleLogicConfig = await LogicAndConditionConfigsLoader.loadScheduleLogic();
                localStorage.setItem('scheduleLogicConfig', JSON.stringify($rootScope.scheduleLogicConfig));
                $rootScope.validationConfig = await LogicAndConditionConfigsLoader.loadValidationConfigs();
                localStorage.setItem('validationConfig', JSON.stringify($rootScope.validationConfig));
                $rootScope.orderSelectorConfig = await LogicAndConditionConfigsLoader.loadOrderSelecterConfigs();
                localStorage.setItem('orderSelectorConfig', JSON.stringify($rootScope.orderSelectorConfig));
                $rootScope.selfUpdatingFields = await LogicAndConditionConfigsLoader.loadSelfUpdatingFieldsConfigs();
                localStorage.setItem('selfUpdatingFields', JSON.stringify($rootScope.selfUpdatingFields));
                $rootScope.fieldsNeedPageRefresh = await LogicAndConditionConfigsLoader.loadFieldsNeedPageRefresh();
                localStorage.setItem('fieldsNeedPageRefresh', JSON.stringify($rootScope.fieldsNeedPageRefresh));
                $rootScope.scoreBasedCalculation = await LogicAndConditionConfigsLoader.loadScoreBasedConfig();
                localStorage.setItem('scoreBasedCalculation', JSON.stringify($rootScope.scoreBasedCalculation));
            } catch (error) {
                console.error('Error loading configs or fetching patient history:', error);
            }
            var config = $q.defer();
            var configNames = ['encounterConfig', 'patientConfig', 'genderMap', 'relationshipTypeMap', 'quickLogoutComboKey', 'contextCookieExpirationTimeInMinutes'];
            configurations.load(configNames).then(function () {
                var conceptConfig = appService.getAppDescriptor().getConfigValue("conceptSetUI");
                var customLocationTags = _.get(conceptConfig, 'facilityLocationTags');
                var hasCustomLocationTags = !_.isEmpty(customLocationTags);
                if (hasCustomLocationTags) {
                    getLocationUuidsFromLocationTags(customLocationTags);
                }
                $rootScope.encounterConfig = angular.extend(new EncounterConfig(), configurations.encounterConfig());
                $rootScope.patientConfig = configurations.patientConfig();
                $rootScope.genderMap = configurations.genderMap();
                $rootScope.relationshipTypeMap = configurations.relationshipTypeMap();
                $rootScope.quickLogoutComboKey = configurations.quickLogoutComboKey() || 'Escape';
                $rootScope.cookieExpiryTime = configurations.contextCookieExpirationTimeInMinutes() || 0;
                config.resolve();
            });
            return config.promise;
        };

        var getLocationUuidsFromLocationTags = function (tags) {
            $rootScope.facilityLocationUuids = [];
            return locationService.getAllByTag(tags, "ANY").then(function (response) {
                $rootScope.facilityLocationUuids = _.map(response.data.results, function (location) {
                    return location.uuid;
                });
            });
        };

        var checkPrivilege = function () {
            return appService.checkPrivilege("app:orders");
        };

        var initApp = function () {
            return appService.initApp('orders', {'app': true, 'extension': true });
        };

        return spinner.forPromise(initApp().then(checkPrivilege).then(getConfigs).then(orderTypeService.loadAll));
    }
]);
