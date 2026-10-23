'use strict';

angular.module('bahmni.clinicalReference')
    .controller('ClinicalReferenceController', ['$scope', '$state',
        function ($scope, $state) {
            $scope.menuItems = [
                { label: 'Drug Search', state: 'dashboard.drugSearch', icon: 'fa-medkit' },
                { label: 'Clinical Calculators', state: 'dashboard.calculators', icon: 'fa-calculator' },
                { label: 'Clinical Guidelines', state: 'dashboard.guidelines', icon: 'fa-book' },
                { label: 'Drug Safety Check', state: 'dashboard.drugCheck', icon: 'fa-shield' }
            ];
            
            $scope.navigateTo = function (state) {
                $state.go(state);
            };
        }
    ]);
