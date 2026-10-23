'use strict';

angular.module('bahmni.ipd')
    .controller('ReferralManagementController', ['$scope', '$http', '$state', '$rootScope', 'spinner', '$bahmniCookieStore',
        function ($scope, $http, $state, $rootScope, spinner, $bahmniCookieStore) {
            $scope.referrals = [];
            $scope.filteredReferrals = [];
            $scope.searchParams = {
                patientName: '',
                mrn: '',
                region: '',
                subcity: '',
                woreda: '',
                referredTo: '',
                department: '',
                diagnosis: '',
                condition: '',
                location: '',
                physician: '',
                status: '',
                dateFrom: '',
                dateTo: ''
            };
            $scope.showFilters = false;
            $scope.sortField = 'referDate';
            $scope.sortReverse = true;

            var locationUuid = $bahmniCookieStore.get(Bahmni.Common.Constants.locationCookieName).uuid;

            $scope.loadReferrals = function () {
                var params = {
                    q: 'emrapi.sqlSearch.referralManagement',
                    v: 'full',
                    location_uuid: locationUuid,
                    provider_uuid: $rootScope.currentProvider ? $rootScope.currentProvider.uuid : ''
                };
                spinner.forPromise($http.get(Bahmni.Common.Constants.sqlUrl, {
                    params: params
                }).then(function (response) {
                    $scope.referrals = response.data || [];
                    $scope.applyFilters();
                }));
            };

            $scope.applyFilters = function () {
                var results = angular.copy($scope.referrals);
                var f = $scope.searchParams;

                if (f.patientName) {
                    var nameLower = f.patientName.toLowerCase();
                    results = results.filter(function (r) {
                        return r.name && r.name.toLowerCase().indexOf(nameLower) !== -1;
                    });
                }
                if (f.mrn) {
                    var mrnLower = f.mrn.toLowerCase();
                    results = results.filter(function (r) {
                        return r.identifier && r.identifier.toLowerCase().indexOf(mrnLower) !== -1;
                    });
                }
                if (f.region) {
                    var regionLower = f.region.toLowerCase();
                    results = results.filter(function (r) {
                        return r.region && r.region.toLowerCase().indexOf(regionLower) !== -1;
                    });
                }
                if (f.subcity) {
                    var subLower = f.subcity.toLowerCase();
                    results = results.filter(function (r) {
                        return r.subcity && r.subcity.toLowerCase().indexOf(subLower) !== -1;
                    });
                }
                if (f.woreda) {
                    var worLower = f.woreda.toLowerCase();
                    results = results.filter(function (r) {
                        return (r.woreda && r.woreda.toLowerCase().indexOf(worLower) !== -1) ||
                               (r.kebele && r.kebele.toLowerCase().indexOf(worLower) !== -1);
                    });
                }
                if (f.referredTo) {
                    var toLower = f.referredTo.toLowerCase();
                    results = results.filter(function (r) {
                        return r.referredTo && r.referredTo.toLowerCase().indexOf(toLower) !== -1;
                    });
                }
                if (f.department) {
                    var deptLower = f.department.toLowerCase();
                    results = results.filter(function (r) {
                        return r.department && r.department.toLowerCase().indexOf(deptLower) !== -1;
                    });
                }
                if (f.diagnosis) {
                    var diagLower = f.diagnosis.toLowerCase();
                    results = results.filter(function (r) {
                        return r.diagnosis && r.diagnosis.toLowerCase().indexOf(diagLower) !== -1;
                    });
                }
                if (f.condition) {
                    var condLower = f.condition.toLowerCase();
                    results = results.filter(function (r) {
                        return r.patientCondition && r.patientCondition.toLowerCase().indexOf(condLower) !== -1;
                    });
                }
                if (f.location) {
                    var locLower = f.location.toLowerCase();
                    results = results.filter(function (r) {
                        return r.location && r.location.toLowerCase().indexOf(locLower) !== -1;
                    });
                }
                if (f.physician) {
                    var phyLower = f.physician.toLowerCase();
                    results = results.filter(function (r) {
                        return r.physicianName && r.physicianName.toLowerCase().indexOf(phyLower) !== -1;
                    });
                }
                if (f.status) {
                    results = results.filter(function (r) {
                        return r.status === f.status;
                    });
                }
                if (f.dateFrom) {
                    var from = new Date(f.dateFrom);
                    results = results.filter(function (r) {
                        return new Date(r.referDate) >= from;
                    });
                }
                if (f.dateTo) {
                    var to = new Date(f.dateTo);
                    to.setHours(23, 59, 59, 999);
                    results = results.filter(function (r) {
                        return new Date(r.referDate) <= to;
                    });
                }

                $scope.filteredReferrals = results;
            };

            $scope.toggleFilters = function () {
                $scope.showFilters = !$scope.showFilters;
            };

            $scope.clearFilters = function () {
                $scope.searchParams = {
                    patientName: '',
                    mrn: '',
                    region: '',
                    subcity: '',
                    woreda: '',
                    referredTo: '',
                    department: '',
                    diagnosis: '',
                    condition: '',
                    location: '',
                    physician: '',
                    status: '',
                    dateFrom: '',
                    dateTo: ''
                };
                $scope.applyFilters();
            };

            $scope.sortBy = function (field) {
                if ($scope.sortField === field) {
                    $scope.sortReverse = !$scope.sortReverse;
                } else {
                    $scope.sortField = field;
                    $scope.sortReverse = false;
                }
            };

            $scope.openPrintForm = function (referral) {
                $state.go('referFormPrint', {
                    patientUuid: referral.patientUuid,
                    visitUuid: referral.visitUuid,
                    providerName: referral.physicianName,
                    physicianName: referral.physicianName,
                    location: referral.location
                });
            };

            $scope.openPatientDashboard = function (referral) {
                $state.go('bedManagement.patient', { patientUuid: referral.patientUuid });
            };

            $scope.getServiceDate = function (ref) {
                if (!ref || !ref.referDate) return '';
                var d;
                if (Array.isArray(ref.referDate)) {
                    d = new Date(ref.referDate[0], ref.referDate[1] - 1, ref.referDate[2], ref.referDate[3] || 0, ref.referDate[4] || 0, ref.referDate[5] || 0);
                } else {
                    d = new Date(ref.referDate);
                }
                if (isNaN(d.getTime())) return '';
                var day = ('0' + d.getDate()).slice(-2);
                var month = ('0' + (d.getMonth() + 1)).slice(-2);
                var year = d.getFullYear();
                return day + '/' + month + '/' + year;
            };

            $scope.getClosedDate = function (ref) {
                if (!ref || !ref.closedDate) return '-';
                var d;
                if (Array.isArray(ref.closedDate)) {
                    d = new Date(ref.closedDate[0], ref.closedDate[1] - 1, ref.closedDate[2], ref.closedDate[3] || 0, ref.closedDate[4] || 0, ref.closedDate[5] || 0);
                } else {
                    d = new Date(ref.closedDate);
                }
                if (isNaN(d.getTime())) return '-';
                var day = ('0' + d.getDate()).slice(-2);
                var month = ('0' + (d.getMonth() + 1)).slice(-2);
                var year = d.getFullYear();
                return day + '/' + month + '/' + year;
            };

            $scope.loadReferrals();
        }
    ]);
