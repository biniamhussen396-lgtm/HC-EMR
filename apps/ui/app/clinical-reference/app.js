'use strict';

angular
    .module('bahmni.clinicalReference', ['ui.router', 'ngCookies'])
    .config(['$urlRouterProvider', '$stateProvider', '$httpProvider', '$compileProvider',
        function ($urlRouterProvider, $stateProvider, $httpProvider, $compileProvider) {
            $httpProvider.defaults.headers.common['Disable-WWW-Authenticate'] = true;

            $urlRouterProvider.otherwise('/dashboard/clinicalReference');

            $stateProvider
            .state('dashboard', {
                url: '/dashboard',
                template: '<div ui-view></div>'
            })
            .state('dashboard.clinicalReference', {
                url: '/clinicalReference',
                templateUrl: 'views/clinicalReference.html',
                controller: 'ClinicalReferenceController'
            })
            .state('dashboard.drugSearch', {
                url: '/drugSearch',
                templateUrl: 'views/drugSearch.html',
                controller: 'DrugSearchController'
            })
            .state('dashboard.calculators', {
                url: '/calculators',
                templateUrl: 'views/calculators.html',
                controller: 'CalculatorsController'
            })
            .state('dashboard.guidelines', {
                url: '/guidelines',
                templateUrl: 'views/guidelines.html',
                controller: 'GuidelinesController'
            })
            .state('dashboard.drugCheck', {
                url: '/drugCheck',
                templateUrl: 'views/drugCheck.html',
                controller: 'DrugCheckController'
            });
        }])
    .filter('unique', function () {
        return function (items, filterOn) {
            if (filterOn === false) return items;
            if ((filterOn || angular.isUndefined(filterOn)) && angular.isArray(items)) {
                var hashCheck = {}, newItems = [];
                var extractValueToCompare = function (item) {
                    if (angular.isObject(item) && angular.isString(filterOn)) {
                        return item[filterOn];
                    }
                    return item;
                };
                angular.forEach(items, function (item) {
                    var valueToCheck = extractValueToCompare(item);
                    if (!hashCheck[valueToCheck]) {
                        hashCheck[valueToCheck] = true;
                        newItems.push(item);
                    }
                });
                return newItems;
            }
            return items;
        };
    });

