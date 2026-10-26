'use strict';

angular.module('bahmni.ipd')
    .controller('ReferralManagementController', ['$scope', '$http', '$state', '$rootScope', 'spinner', '$bahmniCookieStore', '$filter',
        function ($scope, $http, $state, $rootScope, spinner, $bahmniCookieStore, $filter) {
            $scope.referrals = [];
            $scope.filteredReferrals = [];
            $scope.paginatedReferrals = [];
            $scope.pageSize = '10';
            $scope.pageSizeOptions = ['10', '25', '50', '100', 'All'];
            $scope.currentPage = 1;
            $scope.totalPages = 1;
            $scope.startItem = 0;
            $scope.endItem = 0;
            $scope.isPrintingRegister = false;
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
                approvedBy: '',
                approvedSpecialty: '',
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
                if (f.approvedBy) {
                    var apprLower = f.approvedBy.toLowerCase().trim();
                    results = results.filter(function (r) {
                        if (apprLower === 'pending') {
                            return !r.approvedBy || r.approvedBy.trim() === '';
                        }
                        return r.approvedBy && r.approvedBy.toLowerCase().indexOf(apprLower) !== -1;
                    });
                }
                if (f.approvedSpecialty) {
                    var specLower = f.approvedSpecialty.toLowerCase().trim();
                    results = results.filter(function (r) {
                        return r.approvedSpecialty && r.approvedSpecialty.toLowerCase().indexOf(specLower) !== -1;
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
                $scope.currentPage = 1;
                $scope.updatePagination();
            };

            $scope.updatePagination = function () {
                var sorted = $filter('orderBy')($scope.filteredReferrals, $scope.sortField, $scope.sortReverse);
                var total = sorted ? sorted.length : 0;

                if ($scope.pageSize === 'All' || $scope.isPrintingRegister) {
                    $scope.totalPages = 1;
                    $scope.currentPage = 1;
                    $scope.paginatedReferrals = sorted || [];
                    $scope.startItem = total > 0 ? 1 : 0;
                    $scope.endItem = total;
                    return;
                }

                var size = parseInt($scope.pageSize, 10) || 10;
                $scope.totalPages = Math.ceil(total / size) || 1;
                if ($scope.currentPage > $scope.totalPages) {
                    $scope.currentPage = $scope.totalPages;
                }
                if ($scope.currentPage < 1) {
                    $scope.currentPage = 1;
                }

                var startIdx = ($scope.currentPage - 1) * size;
                var endIdx = startIdx + size;
                $scope.paginatedReferrals = (sorted || []).slice(startIdx, endIdx);
                $scope.startItem = total > 0 ? startIdx + 1 : 0;
                $scope.endItem = Math.min(startIdx + size, total);
            };

            $scope.setPage = function (page) {
                if (page < 1 || page > $scope.totalPages || page === $scope.currentPage) {
                    return;
                }
                $scope.currentPage = page;
                $scope.updatePagination();
            };

            $scope.onPageSizeChange = function () {
                $scope.currentPage = 1;
                $scope.updatePagination();
            };

            $scope.getPageNumbers = function () {
                var pages = [];
                var total = $scope.totalPages;
                var current = $scope.currentPage;
                if (total <= 7) {
                    for (var i = 1; i <= total; i++) pages.push(i);
                } else {
                    pages.push(1);
                    var start = Math.max(2, current - 1);
                    var end = Math.min(total - 1, current + 1);
                    if (start > 2) pages.push('...');
                    for (var j = start; j <= end; j++) pages.push(j);
                    if (end < total - 1) pages.push('...');
                    pages.push(total);
                }
                return pages;
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
                    approvedBy: '',
                    approvedSpecialty: '',
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
                $scope.updatePagination();
            };

            $scope.openPrintForm = function (referral) {
                $state.go('referFormPrint', {
                    patientUuid: referral.patientUuid,
                    visitUuid: referral.visitUuid,
                    providerName: referral.physicianName,
                    physicianName: referral.physicianName,
                    location: referral.location,
                    approvedBy: referral.approvedBy,
                    approvedSpecialty: referral.approvedSpecialty,
                    approvalMethod: referral.approvalMethod,
                    approvalDateTime: referral.approvalDateTime,
                    approvalNotes: referral.approvalNotes,
                    patientName: referral.name,
                    identifier: referral.identifier,
                    age: referral.age,
                    sex: referral.sex,
                    woreda: referral.woreda,
                    kebele: referral.kebele,
                    referredTo: referral.referredTo,
                    department: referral.department,
                    diagnosis: referral.diagnosis,
                    patientCondition: referral.patientCondition,
                    reasonForReferral: referral.reasonForReferral,
                    needAmbulance: referral.needAmbulance,
                    needEscorting: referral.needEscorting
                });
            };

            $scope.printRegister = function () {
                var prevSize = $scope.pageSize;
                var prevPage = $scope.currentPage;
                $scope.isPrintingRegister = true;
                $scope.pageSize = 'All';
                $scope.updatePagination();
                setTimeout(function () {
                    window.print();
                    setTimeout(function () {
                        $scope.$apply(function () {
                            $scope.isPrintingRegister = false;
                            $scope.pageSize = prevSize;
                            $scope.currentPage = prevPage;
                            $scope.updatePagination();
                        });
                    }, 500);
                }, 100);
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
