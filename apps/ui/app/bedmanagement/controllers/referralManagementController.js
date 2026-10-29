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
            $scope.isLoading = false;
            $scope.facilityName = 'Boru Meda General Hospital';
            $scope.facilityLogo = '/bahmni_config/openmrs/apps/home/logo.png';
            $scope.ethiopianCurrentDate = toEthiopianDate(new Date());

            // Fetch facility branding dynamically
            $http.get('/bahmni_config/openmrs/apps/home/whiteLabel.json', { ignoreErrors: true }).then(function (response) {
                if (response.data && response.data.homePage) {
                    if (response.data.homePage.logo) {
                        $scope.facilityLogo = response.data.homePage.logo;
                    }
                    if (response.data.homePage.header_text) {
                        var temp = document.createElement('div');
                        temp.innerHTML = response.data.homePage.header_text;
                        var raw = (temp.textContent || temp.innerText || '').trim();
                        raw = raw.replace(/^WELCOME\s*TO\s*/i, '')
                                 .replace(/\s*EMR\s*System\s*$/i, '')
                                 .replace(/\s*EMR\s*$/i, '')
                                 .trim();
                        if (raw) {
                            $scope.facilityName = raw;
                        }
                    }
                }
                var locCookie = $bahmniCookieStore && $bahmniCookieStore.get(Bahmni.Common.Constants.locationCookieName);
                if ((!$scope.facilityName || $scope.facilityName === 'Health Facility') && locCookie && locCookie.name) {
                    $scope.facilityName = locCookie.name;
                }
            }).catch(function () {
                var locCookie = $bahmniCookieStore && $bahmniCookieStore.get(Bahmni.Common.Constants.locationCookieName);
                if (locCookie && locCookie.name) {
                    $scope.facilityName = locCookie.name;
                }
            });

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

            var locCookie = $bahmniCookieStore && $bahmniCookieStore.get(Bahmni.Common.Constants.locationCookieName);
            var locationUuid = locCookie ? locCookie.uuid : '';

            $scope.loadReferrals = function (forceSpinner) {
                $scope.isLoading = true;
                var params = {
                    q: 'emrapi.sqlSearch.referralManagement',
                    v: 'full',
                    location_uuid: locationUuid,
                    provider_uuid: $rootScope.currentProvider ? $rootScope.currentProvider.uuid : ''
                };
                var req = $http.get(Bahmni.Common.Constants.sqlUrl, {
                    params: params
                }).then(function (response) {
                    $scope.referrals = response.data || [];
                    $rootScope.cachedReferrals = $scope.referrals;
                    $scope.applyFilters();
                    $scope.isLoading = false;
                }).catch(function () {
                    $scope.isLoading = false;
                });

                if (forceSpinner || (!$scope.referrals || $scope.referrals.length === 0)) {
                    spinner.forPromise(req);
                }
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

            $scope.exportToExcel = function () {
                var records = $scope.filteredReferrals || [];
                if (!records || records.length === 0) {
                    alert('No referral records available to export.');
                    return;
                }

                var escapeXml = function (val) {
                    if (val === null || val === undefined) return '';
                    return String(val)
                        .replace(/&/g, '&amp;')
                        .replace(/</g, '&lt;')
                        .replace(/>/g, '&gt;')
                        .replace(/"/g, '&quot;')
                        .replace(/'/g, '&apos;');
                };

                var facName = $scope.facilityName || 'Boru Meda General Hospital';
                var curDate = $scope.ethiopianCurrentDate || toEthiopianDate(new Date());

                var xml = '<?xml version="1.0" encoding="UTF-8"?>\r\n' +
                    '<?mso-application progid="Excel.Sheet"?>\r\n' +
                    '<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"\r\n' +
                    ' xmlns:o="urn:schemas-microsoft-com:office:office"\r\n' +
                    ' xmlns:x="urn:schemas-microsoft-com:office:excel"\r\n' +
                    ' xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet"\r\n' +
                    ' xmlns:html="http://www.w3.org/TR/REC-html40">\r\n' +
                    ' <DocumentProperties xmlns="urn:schemas-microsoft-com:office:office">\r\n' +
                    '  <Title>Patient Referral Register</Title>\r\n' +
                    '  <Subject>Liaison Patient Referral Register</Subject>\r\n' +
                    '  <Author>Bahmni EMR</Author>\r\n' +
                    '  <Company>' + escapeXml(facName) + '</Company>\r\n' +
                    ' </DocumentProperties>\r\n' +
                    ' <Styles>\r\n' +
                    '  <Style ss:ID="Default" ss:Name="Normal">\r\n' +
                    '   <Alignment ss:Vertical="Center"/>\r\n' +
                    '   <Borders/>\r\n' +
                    '   <Font ss:FontName="Calibri" ss:Size="10" ss:Color="#000000"/>\r\n' +
                    '   <Interior/>\r\n' +
                    '   <NumberFormat/>\r\n' +
                    '   <Protection/>\r\n' +
                    '  </Style>\r\n' +
                    '  <Style ss:ID="BureauHeader">\r\n' +
                    '   <Alignment ss:Horizontal="Center" ss:Vertical="Center"/>\r\n' +
                    '   <Font ss:FontName="Calibri" ss:Size="11" ss:Bold="1" ss:Color="#444444"/>\r\n' +
                    '  </Style>\r\n' +
                    '  <Style ss:ID="TitleHeader">\r\n' +
                    '   <Alignment ss:Horizontal="Center" ss:Vertical="Center"/>\r\n' +
                    '   <Font ss:FontName="Calibri" ss:Size="14" ss:Bold="1" ss:Color="#1A237E"/>\r\n' +
                    '   <Interior ss:Color="#E8EAF6" ss:Pattern="Solid"/>\r\n' +
                    '  </Style>\r\n' +
                    '  <Style ss:ID="MetaHeader">\r\n' +
                    '   <Alignment ss:Horizontal="Left" ss:Vertical="Center"/>\r\n' +
                    '   <Font ss:FontName="Calibri" ss:Size="9" ss:Italic="1" ss:Color="#333333"/>\r\n' +
                    '  </Style>\r\n' +
                    '  <Style ss:ID="GroupHeader">\r\n' +
                    '   <Alignment ss:Horizontal="Center" ss:Vertical="Center"/>\r\n' +
                    '   <Font ss:FontName="Calibri" ss:Size="10" ss:Bold="1" ss:Color="#0D47A1"/>\r\n' +
                    '   <Interior ss:Color="#BBDEFB" ss:Pattern="Solid"/>\r\n' +
                    '   <Borders>\r\n' +
                    '    <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#1565C0"/>\r\n' +
                    '    <Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#1565C0"/>\r\n' +
                    '    <Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#1565C0"/>\r\n' +
                    '    <Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#1565C0"/>\r\n' +
                    '   </Borders>\r\n' +
                    '  </Style>\r\n' +
                    '  <Style ss:ID="ColHeader">\r\n' +
                    '   <Alignment ss:Horizontal="Center" ss:Vertical="Center" ss:WrapText="1"/>\r\n' +
                    '   <Font ss:FontName="Calibri" ss:Size="9" ss:Bold="1" ss:Color="#FFFFFF"/>\r\n' +
                    '   <Interior ss:Color="#1565C0" ss:Pattern="Solid"/>\r\n' +
                    '   <Borders>\r\n' +
                    '    <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#0D47A1"/>\r\n' +
                    '    <Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#0D47A1"/>\r\n' +
                    '    <Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#0D47A1"/>\r\n' +
                    '    <Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#0D47A1"/>\r\n' +
                    '   </Borders>\r\n' +
                    '  </Style>\r\n' +
                    '  <Style ss:ID="ColNumHeader">\r\n' +
                    '   <Alignment ss:Horizontal="Center" ss:Vertical="Center"/>\r\n' +
                    '   <Font ss:FontName="Calibri" ss:Size="8" ss:Color="#555555"/>\r\n' +
                    '   <Interior ss:Color="#F5F5F5" ss:Pattern="Solid"/>\r\n' +
                    '   <Borders>\r\n' +
                    '    <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#1565C0"/>\r\n' +
                    '    <Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#CCCCCC"/>\r\n' +
                    '    <Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#CCCCCC"/>\r\n' +
                    '    <Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#CCCCCC"/>\r\n' +
                    '   </Borders>\r\n' +
                    '  </Style>\r\n' +
                    '  <Style ss:ID="CellLeft">\r\n' +
                    '   <Alignment ss:Horizontal="Left" ss:Vertical="Center" ss:WrapText="1"/>\r\n' +
                    '   <Font ss:FontName="Calibri" ss:Size="9"/>\r\n' +
                    '   <Borders>\r\n' +
                    '    <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#E0E0E0"/>\r\n' +
                    '    <Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#E0E0E0"/>\r\n' +
                    '    <Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#E0E0E0"/>\r\n' +
                    '    <Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#E0E0E0"/>\r\n' +
                    '   </Borders>\r\n' +
                    '  </Style>\r\n' +
                    '  <Style ss:ID="CellCenter">\r\n' +
                    '   <Alignment ss:Horizontal="Center" ss:Vertical="Center"/>\r\n' +
                    '   <Font ss:FontName="Calibri" ss:Size="9"/>\r\n' +
                    '   <Borders>\r\n' +
                    '    <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#E0E0E0"/>\r\n' +
                    '    <Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#E0E0E0"/>\r\n' +
                    '    <Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#E0E0E0"/>\r\n' +
                    '    <Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#E0E0E0"/>\r\n' +
                    '   </Borders>\r\n' +
                    '  </Style>\r\n' +
                    '  <Style ss:ID="CellAltLeft">\r\n' +
                    '   <Alignment ss:Horizontal="Left" ss:Vertical="Center" ss:WrapText="1"/>\r\n' +
                    '   <Font ss:FontName="Calibri" ss:Size="9"/>\r\n' +
                    '   <Interior ss:Color="#F9FAFB" ss:Pattern="Solid"/>\r\n' +
                    '   <Borders>\r\n' +
                    '    <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#E0E0E0"/>\r\n' +
                    '    <Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#E0E0E0"/>\r\n' +
                    '    <Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#E0E0E0"/>\r\n' +
                    '    <Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#E0E0E0"/>\r\n' +
                    '   </Borders>\r\n' +
                    '  </Style>\r\n' +
                    '  <Style ss:ID="CellAltCenter">\r\n' +
                    '   <Alignment ss:Horizontal="Center" ss:Vertical="Center"/>\r\n' +
                    '   <Font ss:FontName="Calibri" ss:Size="9"/>\r\n' +
                    '   <Interior ss:Color="#F9FAFB" ss:Pattern="Solid"/>\r\n' +
                    '   <Borders>\r\n' +
                    '    <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#E0E0E0"/>\r\n' +
                    '    <Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#E0E0E0"/>\r\n' +
                    '    <Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#E0E0E0"/>\r\n' +
                    '    <Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#E0E0E0"/>\r\n' +
                    '   </Borders>\r\n' +
                    '  </Style>\r\n' +
                    '  <Style ss:ID="StatusOpen">\r\n' +
                    '   <Alignment ss:Horizontal="Center" ss:Vertical="Center"/>\r\n' +
                    '   <Font ss:FontName="Calibri" ss:Size="9" ss:Bold="1" ss:Color="#2E7D32"/>\r\n' +
                    '   <Interior ss:Color="#E8F5E9" ss:Pattern="Solid"/>\r\n' +
                    '   <Borders>\r\n' +
                    '    <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#C8E6C9"/>\r\n' +
                    '    <Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#C8E6C9"/>\r\n' +
                    '    <Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#C8E6C9"/>\r\n' +
                    '    <Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#C8E6C9"/>\r\n' +
                    '   </Borders>\r\n' +
                    '  </Style>\r\n' +
                    '  <Style ss:ID="StatusClosed">\r\n' +
                    '   <Alignment ss:Horizontal="Center" ss:Vertical="Center"/>\r\n' +
                    '   <Font ss:FontName="Calibri" ss:Size="9" ss:Color="#607D8B"/>\r\n' +
                    '   <Interior ss:Color="#ECEFF1" ss:Pattern="Solid"/>\r\n' +
                    '   <Borders>\r\n' +
                    '    <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#CFD8DC"/>\r\n' +
                    '    <Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#CFD8DC"/>\r\n' +
                    '    <Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#CFD8DC"/>\r\n' +
                    '    <Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#CFD8DC"/>\r\n' +
                    '   </Borders>\r\n' +
                    '  </Style>\r\n' +
                    ' </Styles>\r\n' +
                    ' <Worksheet ss:Name="Referral Register">\r\n' +
                    '  <Table>\r\n';

                var colWidths = [
                    35,  // S/N
                    75,  // Service Date (E.C.)
                    65,  // MRN
                    150, // Name
                    35,  // Age
                    35,  // Sex
                    70,  // Region
                    75,  // Subcity
                    80,  // Woreda
                    65,  // Kebele
                    45,  // Referral In
                    45,  // Referral Out
                    130, // Referred To Facility
                    75,  // Case Type
                    150, // Diagnosis
                    90,  // Department
                    90,  // Location
                    130, // Physician Referred By
                    130, // Approved By
                    95,  // Specialty
                    95,  // Approval Method
                    105, // Approval DateTime (E.C.)
                    140, // Reason for Referral
                    55,  // Ambulance
                    55,  // Escort
                    60   // Status
                ];

                colWidths.forEach(function (w) {
                    xml += '   <Column ss:Width="' + w + '"/>\r\n';
                });

                var totalCols = colWidths.length;

                // Title row 1: Regional bureau
                xml += '   <Row ss:Height="20">\r\n' +
                    '    <Cell ss:MergeAcross="' + (totalCols - 1) + '" ss:StyleID="BureauHeader">' +
                    '<Data ss:Type="String">AMHARA NATIONAL REGIONAL STATE HEALTH BUREAU</Data></Cell>\r\n' +
                    '   </Row>\r\n';

                // Title row 2: Facility name and Register title
                xml += '   <Row ss:Height="26">\r\n' +
                    '    <Cell ss:MergeAcross="' + (totalCols - 1) + '" ss:StyleID="TitleHeader">' +
                    '<Data ss:Type="String">' + escapeXml(facName.toUpperCase()) + ' - LIAISON PATIENT REFERRAL REGISTER (IN / OUT)</Data></Cell>\r\n' +
                    '   </Row>\r\n';

                // Metadata row 3
                xml += '   <Row ss:Height="18">\r\n' +
                    '    <Cell ss:MergeAcross="' + (totalCols - 1) + '" ss:StyleID="MetaHeader">' +
                    '<Data ss:Type="String">Date (E.C.): ' + escapeXml(curDate) +
                    '   |   Total Filtered Records: ' + records.length +
                    ($scope.searchParams.status ? ('   |   Status: ' + escapeXml($scope.searchParams.status)) : '') +
                    '</Data></Cell>\r\n' +
                    '   </Row>\r\n';

                // Blank row
                xml += '   <Row ss:Height="8"/>\r\n';

                // Group headers (Row 5)
                xml += '   <Row ss:Height="22">\r\n' +
                    '    <Cell ss:MergeAcross="5" ss:StyleID="GroupHeader"><Data ss:Type="String">Identification</Data></Cell>\r\n' +
                    '    <Cell ss:Index="7" ss:MergeAcross="3" ss:StyleID="GroupHeader"><Data ss:Type="String">Address</Data></Cell>\r\n' +
                    '    <Cell ss:Index="11" ss:MergeAcross="1" ss:StyleID="GroupHeader"><Data ss:Type="String">Type of Referral</Data></Cell>\r\n' +
                    '    <Cell ss:Index="13" ss:MergeAcross="13" ss:StyleID="GroupHeader"><Data ss:Type="String">Referral Service Details</Data></Cell>\r\n' +
                    '   </Row>\r\n';

                // Column Headers (Row 6)
                var headers = [
                    'S/N', 'Service Date (E.C.)', 'MRN', 'Name of the Patient', 'Age', 'Sex',
                    'Region', 'Subcity/Zone', 'Woreda', 'Kebele',
                    'In', 'Out',
                    'Referred To Facility', 'Type of Case', 'Diagnosis', 'Department', 'Location',
                    'Physician (Referred by)', 'Approved By', 'Specialty', 'Approval Method',
                    'Approval Date (E.C.)', 'Reason for Referral', 'Ambulance', 'Escort', 'Status'
                ];

                xml += '   <Row ss:Height="24">\r\n';
                headers.forEach(function (h) {
                    xml += '    <Cell ss:StyleID="ColHeader"><Data ss:Type="String">' + escapeXml(h) + '</Data></Cell>\r\n';
                });
                xml += '   </Row>\r\n';

                // Column Numbers (Row 7)
                xml += '   <Row ss:Height="14">\r\n';
                headers.forEach(function (h, i) {
                    xml += '    <Cell ss:StyleID="ColNumHeader"><Data ss:Type="String">(' + (i + 1) + ')</Data></Cell>\r\n';
                });
                xml += '   </Row>\r\n';

                // Data Rows
                records.forEach(function (ref, index) {
                    var isAlt = (index % 2 === 1);
                    var styleLeft = isAlt ? 'CellAltLeft' : 'CellLeft';
                    var styleCenter = isAlt ? 'CellAltCenter' : 'CellCenter';

                    var sDate = $scope.getServiceDate(ref);
                    var appDate = ref.approvalDateTime ? toEthiopianDateTime(ref.approvalDateTime) : '';
                    var statusStyle = (ref.status === 'Closed') ? 'StatusClosed' : 'StatusOpen';

                    xml += '   <Row ss:Height="19">\r\n';
                    xml += '    <Cell ss:StyleID="' + styleCenter + '"><Data ss:Type="Number">' + (index + 1) + '</Data></Cell>\r\n';
                    xml += '    <Cell ss:StyleID="' + styleCenter + '"><Data ss:Type="String">' + escapeXml(sDate) + '</Data></Cell>\r\n';
                    xml += '    <Cell ss:StyleID="' + styleCenter + '"><Data ss:Type="String">' + escapeXml(ref.identifier || '') + '</Data></Cell>\r\n';
                    xml += '    <Cell ss:StyleID="' + styleLeft + '"><Data ss:Type="String">' + escapeXml(ref.name || '') + '</Data></Cell>\r\n';
                    xml += '    <Cell ss:StyleID="' + styleCenter + '"><Data ss:Type="' + (ref.age !== undefined && ref.age !== null && ref.age !== '' ? 'Number' : 'String') + '">' + (ref.age !== undefined && ref.age !== null ? ref.age : '') + '</Data></Cell>\r\n';
                    xml += '    <Cell ss:StyleID="' + styleCenter + '"><Data ss:Type="String">' + escapeXml(ref.sex === 'Male' ? 'M' : (ref.sex === 'Female' ? 'F' : (ref.sex || ''))) + '</Data></Cell>\r\n';
                    xml += '    <Cell ss:StyleID="' + styleLeft + '"><Data ss:Type="String">' + escapeXml(ref.region || '') + '</Data></Cell>\r\n';
                    xml += '    <Cell ss:StyleID="' + styleLeft + '"><Data ss:Type="String">' + escapeXml(ref.subcity || '') + '</Data></Cell>\r\n';
                    xml += '    <Cell ss:StyleID="' + styleLeft + '"><Data ss:Type="String">' + escapeXml(ref.woreda || '') + '</Data></Cell>\r\n';
                    xml += '    <Cell ss:StyleID="' + styleCenter + '"><Data ss:Type="String">' + escapeXml(ref.kebele || '') + '</Data></Cell>\r\n';
                    xml += '    <Cell ss:StyleID="' + styleCenter + '"><Data ss:Type="String">' + (ref.referralDirection === 'In' ? 'Yes' : '') + '</Data></Cell>\r\n';
                    xml += '    <Cell ss:StyleID="' + styleCenter + '"><Data ss:Type="String">' + (ref.referralDirection === 'Out' ? 'Yes' : '') + '</Data></Cell>\r\n';
                    xml += '    <Cell ss:StyleID="' + styleLeft + '"><Data ss:Type="String">' + escapeXml(ref.referredTo || '') + '</Data></Cell>\r\n';
                    xml += '    <Cell ss:StyleID="' + styleCenter + '"><Data ss:Type="String">' + escapeXml(ref.patientCondition || '') + '</Data></Cell>\r\n';
                    xml += '    <Cell ss:StyleID="' + styleLeft + '"><Data ss:Type="String">' + escapeXml(ref.diagnosis || '') + '</Data></Cell>\r\n';
                    xml += '    <Cell ss:StyleID="' + styleLeft + '"><Data ss:Type="String">' + escapeXml(ref.department || '') + '</Data></Cell>\r\n';
                    xml += '    <Cell ss:StyleID="' + styleLeft + '"><Data ss:Type="String">' + escapeXml(ref.location || '') + '</Data></Cell>\r\n';
                    xml += '    <Cell ss:StyleID="' + styleLeft + '"><Data ss:Type="String">' + escapeXml(ref.physicianName || '') + '</Data></Cell>\r\n';
                    xml += '    <Cell ss:StyleID="' + styleLeft + '"><Data ss:Type="String">' + escapeXml(ref.approvedBy || 'Pending') + '</Data></Cell>\r\n';
                    xml += '    <Cell ss:StyleID="' + styleLeft + '"><Data ss:Type="String">' + escapeXml(ref.approvedSpecialty || '') + '</Data></Cell>\r\n';
                    xml += '    <Cell ss:StyleID="' + styleCenter + '"><Data ss:Type="String">' + escapeXml(ref.approvalMethod || '') + '</Data></Cell>\r\n';
                    xml += '    <Cell ss:StyleID="' + styleCenter + '"><Data ss:Type="String">' + escapeXml(appDate) + '</Data></Cell>\r\n';
                    xml += '    <Cell ss:StyleID="' + styleLeft + '"><Data ss:Type="String">' + escapeXml(ref.reasonForReferral || '') + '</Data></Cell>\r\n';
                    xml += '    <Cell ss:StyleID="' + styleCenter + '"><Data ss:Type="String">' + (ref.needAmbulance ? 'Yes' : 'No') + '</Data></Cell>\r\n';
                    xml += '    <Cell ss:StyleID="' + styleCenter + '"><Data ss:Type="String">' + (ref.needEscorting ? 'Yes' : 'No') + '</Data></Cell>\r\n';
                    xml += '    <Cell ss:StyleID="' + statusStyle + '"><Data ss:Type="String">' + escapeXml(ref.status || 'Open') + '</Data></Cell>\r\n';
                    xml += '   </Row>\r\n';
                });

                xml += '  </Table>\r\n' +
                    ' </Worksheet>\r\n' +
                    '</Workbook>';

                var dateStr = (curDate || '').replace(/[\/\\]/g, '-');
                var fileName = 'Referral_Register_' + (dateStr || 'export') + '.xls';

                var blob = new Blob([xml], { type: 'application/vnd.ms-excel;charset=utf-8;' });
                if (window.navigator && window.navigator.msSaveOrOpenBlob) {
                    window.navigator.msSaveOrOpenBlob(blob, fileName);
                } else {
                    var link = document.createElement('a');
                    var url = URL.createObjectURL(blob);
                    link.href = url;
                    link.download = fileName;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    setTimeout(function () {
                        URL.revokeObjectURL(url);
                    }, 1000);
                }
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

            // Instant render from cache if available
            if ($rootScope.cachedReferrals && $rootScope.cachedReferrals.length > 0) {
                $scope.referrals = $rootScope.cachedReferrals;
                $scope.applyFilters();
            }

            $scope.loadReferrals();
        }
    ]);
