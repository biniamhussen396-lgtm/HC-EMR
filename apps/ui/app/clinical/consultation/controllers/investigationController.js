'use strict';

angular.module('bahmni.clinical')
.controller('InvestigationController', ['$scope', '$http', 'labTestsProvider', 'otherTestsProvider',
    function ($scope, $http, labTestsProvider, otherTestsProvider) {
        $scope.tabs = [
        {name: 'Laboratory', testsProvider: labTestsProvider, filterColumn: "sample", filterHeader: "Sample", categoryColumn: "department"},
        {name: 'Other', testsProvider: otherTestsProvider, filterColumn: "type", filterHeader: "Investigation", categoryColumn: "category"}
        ];

        $scope.labLocations = [];
        $scope.locationData = { selectedLabLocation: null };

        $scope.fetchLabLocations = function () {
            var url = '/openelis/pages/location/labLocationList.jsp';
            $http.get(url, { ignoreErrors: true }).catch(function () {
                return $http.get('/openelis/LabLocationList.do', { ignoreErrors: true });
            }).then(function (response) {
                $scope.labLocations = (response && response.data && response.data.locations) || [];
                var savedId = localStorage.getItem('selectedLabLocationId');
                if (savedId && $scope.labLocations.length > 0) {
                    var exists = $scope.labLocations.some(function (l) { return l.id === parseInt(savedId); });
                    if (exists) {
                        $scope.locationData.selectedLabLocation = parseInt(savedId);
                        $scope.consultation.labLocationId = $scope.locationData.selectedLabLocation;
                        $scope.consultation.labLocationName = localStorage.getItem('selectedLabLocationName');
                    }
                }
            }).catch(function (err) {
                console.error('Failed to load lab locations', err);
            });
        };

        $scope.onLabLocationChange = function () {
            if ($scope.locationData.selectedLabLocation) {
                var loc = _.find($scope.labLocations, {id: $scope.locationData.selectedLabLocation});
                if (loc) {
                    $scope.consultation.labLocationId = $scope.locationData.selectedLabLocation;
                    $scope.consultation.labLocationName = loc.name;
                    localStorage.setItem('selectedLabLocationId', $scope.locationData.selectedLabLocation);
                    localStorage.setItem('selectedLabLocationName', loc.name);
                }
            } else {
                $scope.consultation.labLocationId = null;
                $scope.consultation.labLocationName = null;
            }
        };

        $scope.fetchLabLocations();

        $scope.activateTab = function (tab) {
            if ($scope.activeTab) {
                ($scope.activeTab.klass = "");
            }
            $scope.activeTab = tab;
            $scope.activeTab.klass = "active";
        };

        var findVoidedInvestigations = function () {
            var filteredInvestigation = $scope.consultation.investigations.filter(function (investigation) {
                return investigation.voided;
            });
            return filteredInvestigation.length === $scope.consultation.investigations.length;
        };
        $scope.isValidInvestigation = function () {
            if (!$scope.consultation.investigations.length > 0 || findVoidedInvestigations()) {
                $scope.noteState = false;
                if ($scope.consultation.labOrderNote.uuid) {
                    $scope.consultation.labOrderNote.voided = true;
                } else {
                    if ($scope.consultation.labOrderNote.value) {
                        $scope.consultation.labOrderNote.value = null;
                    }
                }
                return false;
            } else {
                if ($scope.consultation.labOrderNote.uuid) {
                    $scope.noteState = true;
                    $scope.consultation.labOrderNote.voided = false;
                }
                return true;
            }
        };

        $scope.activateTab($scope.tabs[0]);

        $scope.toggleNote = function () {
            $scope.noteState = $scope.noteState ? false : true;
        };

        var init = function () {
            $scope.noteState = $scope.consultation.labOrderNote && $scope.consultation.labOrderNote.value ? true : false;
        };

        $scope.onNoteChanged = function () {
            if ($scope.consultation.labOrderNote) {
//        TODO: Mihir, D3 : Hacky fix to update the datetime to current datetime on the server side. Ideal would be void the previous observation and create a new one.
                $scope.consultation.labOrderNote.observationDateTime = null;
            }
        };

        init();
    }]);
