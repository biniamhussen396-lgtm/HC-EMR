'use strict';

/**
 * Bahmni Register Application Module
 */
angular
    .module('bahmni.register', ['ui.router', 'ngCookies'])
    .config(['$urlRouterProvider', '$stateProvider', '$httpProvider', '$compileProvider',
        function ($urlRouterProvider, $stateProvider, $httpProvider, $compileProvider) {
            $httpProvider.defaults.headers.common['Disable-WWW-Authenticate'] = true;

            $urlRouterProvider.otherwise('/dashboard/register');

            $stateProvider
                .state('dashboard', {
                    url: '/dashboard',
                    template: '<div ui-view></div>'
                })
                .state('dashboard.register', {
                    url: '/register',
                    templateUrl: 'views/register.html',
                    controller: 'RegisterController'
                });
        }])
    .filter('filterDictionary', function () {
        return function (items, searchText) {
            if (!searchText) return items;
            var q = searchText.toLowerCase();
            return (items || []).filter(function (item) {
                return (item.name && item.name.toLowerCase().indexOf(q) !== -1) ||
                    (item.form && item.form.toLowerCase().indexOf(q) !== -1) ||
                    (item.concept && item.concept.toLowerCase().indexOf(q) !== -1) ||
                    (item.rule && item.rule.toLowerCase().indexOf(q) !== -1);
            });
        };
    });
