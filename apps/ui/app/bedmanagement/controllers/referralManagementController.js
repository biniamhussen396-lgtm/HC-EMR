'use strict';

angular.module('bahmni.ipd')
    .controller('ReferralManagementController', ['$scope', '$http', '$state', '$rootScope', 'spinner', '$bahmniCookieStore', '$filter', '$injector',
        function ($scope, $http, $state, $rootScope, spinner, $bahmniCookieStore, $filter, $injector) {
            var ethiopianService = $injector.has('ethiopianGregorianService') ? $injector.get('ethiopianGregorianService') : null;

            var toEthiopianDate = function (gregDate) {
                if (!gregDate) return '';
                if (typeof gregDate === 'string' && /^\d{1,2}\/\d{1,2}\/\d{4}$/.test(gregDate.trim())) {
                    var p = gregDate.trim().split('/');
                    var yr = parseInt(p[2], 10);
                    if (yr >= 1900 && yr <= 2050 && parseInt(p[1], 10) <= 13) {
                        return gregDate.trim();
                    }
                }
                var d;
                if (Array.isArray(gregDate)) {
                    d = new Date(gregDate[0], gregDate[1] - 1, gregDate[2], gregDate[3] || 0, gregDate[4] || 0, gregDate[5] || 0);
                } else if (gregDate instanceof Date) {
                    d = gregDate;
                } else {
                    d = new Date(gregDate);
                }
                if (isNaN(d.getTime())) return typeof gregDate === 'string' ? gregDate : '';

                if (ethiopianService && typeof ethiopianService.gregToEth === 'function') {
                    try {
                        var ethStr = ethiopianService.gregToEth((d.getMonth() + 1) + '/' + d.getDate() + '/' + d.getFullYear());
                        if (ethStr) return ethStr;
                    } catch (e) {}
                }

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
                return ddStr + '/' + mmStr + '/' + ethYear;
            };

            var toEthiopianDateTime = function (dtInput) {
                if (!dtInput) return '';
                var d = new Date(dtInput);
                if (isNaN(d.getTime())) {
                    return dtInput;
                }
                var ethD = toEthiopianDate(d);
                var hh = ('0' + d.getHours()).slice(-2);
                var min = ('0' + d.getMinutes()).slice(-2);
                return ethD + ' ' + hh + ':' + min;
            };

            $scope.formatApprovalDateTime = function (dt) {
                return toEthiopianDateTime(dt);
            };

            var parseDateValue = function (val) {
                if (!val) return null;
                if (val instanceof Date) return isNaN(val.getTime()) ? null : val;
                if (typeof val === 'string') {
                    var s = val.trim();
                    if (/^\d{1,2}\/\d{1,2}\/\d{4}$/.test(s)) {
                        if (ethiopianService && typeof ethiopianService.ethToGreg === 'function') {
                            try {
                                var g = ethiopianService.ethToGreg(s);
                                if (g) {
                                    var pd = new Date(g);
                                    if (!isNaN(pd.getTime())) return pd;
                                }
                            } catch (e) {}
                        }
                        var parts = s.split('/');
                        var ed = parseInt(parts[0], 10), em = parseInt(parts[1], 10), ey = parseInt(parts[2], 10);
                        if (!isNaN(ed) && !isNaN(em) && !isNaN(ey)) {
                            var gy = ey + 7;
                            var isGregLeap = (gy % 4 === 0 && gy % 100 !== 0) || gy % 400 === 0;
                            var ethNewYear = new Date(gy, 8, isGregLeap ? 12 : 11);
                            var daysElapsed = (em - 1) * 30 + (ed - 1);
                            var gd = new Date(ethNewYear.getTime() + daysElapsed * 86400000);
                            if (!isNaN(gd.getTime())) return gd;
                        }
                    }
                    var direct = new Date(s);
                    if (!isNaN(direct.getTime())) return direct;
                }
                return null;
            };

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
                dateFrom: null,
                dateTo: null
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
                    var from = parseDateValue(f.dateFrom);
                    if (from) {
                        from.setHours(0, 0, 0, 0);
                        results = results.filter(function (r) {
                            var rd = Array.isArray(r.referDate) ?
                                new Date(r.referDate[0], r.referDate[1] - 1, r.referDate[2]) :
                                new Date(r.referDate);
                            return rd >= from;
                        });
                    }
                }
                if (f.dateTo) {
                    var to = parseDateValue(f.dateTo);
                    if (to) {
                        to.setHours(23, 59, 59, 999);
                        results = results.filter(function (r) {
                            var rd = Array.isArray(r.referDate) ?
                                new Date(r.referDate[0], r.referDate[1] - 1, r.referDate[2]) :
                                new Date(r.referDate);
                            return rd <= to;
                        });
                    }
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
                    dateFrom: null,
                    dateTo: null
                };
                if (window.jQuery) {
                    window.jQuery('.filter-group ethiopian-date-selector input').val('');
                }
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
                    needEscorting: referral.needEscorting,
                    referDate: $scope.getServiceDate(referral)
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
                return toEthiopianDate(ref.referDate);
            };

            $scope.getClosedDate = function (ref) {
                if (!ref || !ref.closedDate) return '-';
                return toEthiopianDate(ref.closedDate);
            };

            $scope.loadReferrals();
        }
    ]);
