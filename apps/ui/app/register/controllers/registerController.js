'use strict';

/**
 * Register Controller
 * Coordinates dynamic template switching, summary metric KPI calculations,
 * comprehensive filtering, Ethiopian Calendar support, MOH-standard data export,
 * interactive Ethiopian Calendar Datepicker, configurable table pagination,
 * and multiselect filtering for OPD Locations and IPD Wards.
 */
angular.module('bahmni.register')
    .controller('RegisterController', [
        '$scope', '$http', '$filter', '$timeout', '$window', 'registerService', 'ethiopianCalendarService',
        function ($scope, $http, $filter, $timeout, $window, registerService, ethiopianCalendarService) {

            // Access Control State
            $scope.isAuthorized = null; // null: checking, true: granted, false: denied
            $scope.isAuthChecking = true;
            $scope.accessError = '';
            $scope.currentUser = null;

            // Facility Information
            $scope.facilityName = 'Boru Meda General Hospital';
            $scope.facilitySubtext = 'Federal Democratic Republic of Ethiopia — Ministry of Health';
            $scope.facilityLogo = '../images/bahmniLogo.png';

            // Current Ethiopian Date Header
            var currentEth = ethiopianCalendarService.getCurrentEthDate();
            $scope.currentEthDate = currentEth ? currentEth.formatted : '';
            $scope.currentEthFull = currentEth ? currentEth.formattedFull : '';

            // Register Options
            $scope.availableRegisters = [
                { id: 'ICU', name: 'Intensive Care Unit (ICU) Register', shortName: 'ICU Register', icon: 'fa-heartbeat', cols: 26, badge: 'MOH 26-Cols' },
                { id: 'OPD', name: 'Out Patient Department (OPD) Register', shortName: 'OPD Register', icon: 'fa-stethoscope', cols: 23, badge: 'MOH 23-Cols' },
                { id: 'LIAISON', name: 'Liaison Referral-in/out Register', shortName: 'Liaison Register', icon: 'fa-exchange', cols: 21, badge: 'MOH 21-Cols' },
                { id: 'IPD', name: 'Inpatient (IPD) Admission/Discharge Register', shortName: 'IPD Register', icon: 'fa-bed', cols: 27, badge: 'MOH 27-Cols' }
            ];

            $scope.activeRegister = 'ICU'; // Default active template
            $scope.activeRegisterMeta = $scope.availableRegisters[0];

            // Data state
            $scope.rawRecords = [];
            $scope.filteredRecords = [];
            $scope.pagedRecords = [];
            $scope.isLoading = false;
            $scope.isReferenceOpen = false;
            $scope.referenceSearchText = '';
            $scope.conceptDictionary = [];

            // Filter state
            $scope.opdLocations = [];
            $scope.ipdWards = [];
            $scope.filters = {
                search: '',
                dateRangeKey: 'TODAY',
                fromEthDate: '',
                toEthDate: '',
                sex: '',
                ageGroup: '',
                // ICU specific
                icuVentilation: '',
                icuOutcome: '',
                icuVap: '',
                icuReadmission: '',
                // OPD specific
                visitLocation: '',
                selectedLocations: [],
                opdStatus: '',
                opdRta: '',
                opdTb: '',
                opdHiv: '',
                // Liaison specific
                liaisonType: '',
                liaisonCaseType: '',
                liaisonAmbulance: '',
                liaisonFeedback: '',
                // IPD specific
                ipdWard: '',
                selectedWards: [],
                ipdStatus: ''
            };

            // Predefined Ethiopian Date Ranges
            $scope.predefinedRanges = ethiopianCalendarService.getPredefinedRanges();

            // Dynamic KPI Summaries
            $scope.kpis = {};

            // =========================================================================
            // Multiselect Dropdown State & Controls (Location & Ward)
            // =========================================================================
            $scope.multiselectOpen = null; // 'location' or 'ward' or null
            $scope.locationSearchText = '';
            $scope.wardSearchText = '';

            $scope.toggleMultiselect = function (type, $event) {
                if ($event) $event.stopPropagation();
                if ($scope.multiselectOpen === type) {
                    $scope.multiselectOpen = null;
                } else {
                    $scope.multiselectOpen = type;
                    $scope.ethPicker.isOpen = false;
                }
            };

            $scope.closeMultiselect = function () {
                $scope.multiselectOpen = null;
            };

            $scope.getLocationDropdownLabel = function () {
                var selected = $scope.filters.selectedLocations || [];
                if (selected.length === 0) {
                    return 'Location: All (' + ($scope.opdLocations.length || 0) + ')';
                }
                if (selected.length === 1) {
                    return 'Location: ' + selected[0];
                }
                return 'Locations: ' + selected.length + ' selected';
            };

            $scope.isLocationSelected = function (loc) {
                return ($scope.filters.selectedLocations || []).indexOf(loc) !== -1;
            };

            $scope.toggleLocationItem = function (loc, $event) {
                if ($event) $event.stopPropagation();
                if (!$scope.filters.selectedLocations) $scope.filters.selectedLocations = [];
                var idx = $scope.filters.selectedLocations.indexOf(loc);
                if (idx === -1) {
                    $scope.filters.selectedLocations.push(loc);
                } else {
                    $scope.filters.selectedLocations.splice(idx, 1);
                }
                $scope.applyFilters();
            };

            $scope.selectAllLocations = function ($event) {
                if ($event) $event.stopPropagation();
                $scope.filters.selectedLocations = angular.copy($scope.opdLocations);
                $scope.applyFilters();
            };

            $scope.clearAllLocations = function ($event) {
                if ($event) $event.stopPropagation();
                $scope.filters.selectedLocations = [];
                $scope.applyFilters();
            };

            $scope.getWardDropdownLabel = function () {
                var selected = $scope.filters.selectedWards || [];
                if (selected.length === 0) {
                    return 'Ward: All (' + ($scope.ipdWards.length || 0) + ')';
                }
                if (selected.length === 1) {
                    return 'Ward: ' + selected[0];
                }
                return 'Wards: ' + selected.length + ' selected';
            };

            $scope.isWardSelected = function (w) {
                return ($scope.filters.selectedWards || []).indexOf(w) !== -1;
            };

            $scope.toggleWardItem = function (w, $event) {
                if ($event) $event.stopPropagation();
                if (!$scope.filters.selectedWards) $scope.filters.selectedWards = [];
                var idx = $scope.filters.selectedWards.indexOf(w);
                if (idx === -1) {
                    $scope.filters.selectedWards.push(w);
                } else {
                    $scope.filters.selectedWards.splice(idx, 1);
                }
                $scope.applyFilters();
            };

            $scope.selectAllWards = function ($event) {
                if ($event) $event.stopPropagation();
                $scope.filters.selectedWards = angular.copy($scope.ipdWards);
                $scope.applyFilters();
            };

            $scope.clearAllWards = function ($event) {
                if ($event) $event.stopPropagation();
                $scope.filters.selectedWards = [];
                $scope.applyFilters();
            };

            // =========================================================================
            // Pagination State & Controls (Default: 10 rows with customization)
            // =========================================================================
            $scope.pagination = {
                pageSize: 10,
                currentPage: 1,
                pageSizeOptions: [10, 25, 50, 100, 250, 'All']
            };
            $scope.totalPages = 1;
            $scope.startIndex = 0;
            $scope.endIndex = 0;

            $scope.updatePagination = function () {
                var total = ($scope.filteredRecords || []).length;
                var size = $scope.pagination.pageSize === 'All' ? total : parseInt($scope.pagination.pageSize, 10);
                if (isNaN(size) || size <= 0) size = total > 0 ? total : 10;
                $scope.totalPages = Math.ceil(total / size) || 1;
                if ($scope.pagination.currentPage > $scope.totalPages) {
                    $scope.pagination.currentPage = 1;
                }
                if ($scope.pagination.currentPage < 1) {
                    $scope.pagination.currentPage = 1;
                }
                var start = ($scope.pagination.currentPage - 1) * size;
                var end = Math.min(start + size, total);
                $scope.startIndex = total > 0 ? start : 0;
                $scope.endIndex = end;
                $scope.pagedRecords = $scope.filteredRecords.slice(start, end);
            };

            $scope.goToPage = function (page) {
                if (page < 1 || page > $scope.totalPages) return;
                $scope.pagination.currentPage = page;
                $scope.updatePagination();
            };

            $scope.nextPage = function () {
                if ($scope.pagination.currentPage < $scope.totalPages) {
                    $scope.goToPage($scope.pagination.currentPage + 1);
                }
            };

            $scope.prevPage = function () {
                if ($scope.pagination.currentPage > 1) {
                    $scope.goToPage($scope.pagination.currentPage - 1);
                }
            };

            $scope.changePageSize = function (newSize) {
                $scope.pagination.pageSize = newSize;
                $scope.pagination.currentPage = 1;
                $scope.updatePagination();
            };

            $scope.getPageNumbers = function () {
                var pages = [];
                var current = $scope.pagination.currentPage;
                var total = $scope.totalPages;
                var start = Math.max(1, current - 2);
                var end = Math.min(total, current + 2);
                for (var i = start; i <= end; i++) {
                    pages.push(i);
                }
                return pages;
            };

            // =========================================================================
            // Interactive Ethiopian Calendar Datepicker Widget
            // =========================================================================
            $scope.ethPicker = {
                isOpen: false,
                activeField: null, // 'fromEthDate' or 'toEthDate'
                year: 2019,
                month: 2, // 1-13 (Tikimt = 2)
                amharicMonths: ethiopianCalendarService.amharicMonths,
                englishMonths: ethiopianCalendarService.englishMonths,
                weekDays: ["እሑ", "ሰኞ", "ማክ", "ረቡ", "ሐሙ", "ዓር", "ቅዳ"],
                daysGrid: [],
                leadingBlanks: []
            };

            function parseEthDateString(str) {
                if (!str || typeof str !== 'string') return null;
                var p = str.trim().split('/');
                if (p.length !== 3) p = str.trim().split('-');
                if (p.length !== 3) return null;
                var day = parseInt(p[0], 10);
                var month = parseInt(p[1], 10);
                var year = parseInt(p[2], 10);
                if (isNaN(day) || isNaN(month) || isNaN(year)) return null;
                return { day: day, month: month, year: year };
            }

            $scope.openEthPicker = function (field, $event) {
                if ($event) $event.stopPropagation();
                $scope.ethPicker.activeField = field;
                var currentVal = $scope.filters[field];
                var parsed = parseEthDateString(currentVal);
                if (parsed) {
                    $scope.ethPicker.year = parsed.year;
                    $scope.ethPicker.month = parsed.month;
                } else {
                    var ethToday = ethiopianCalendarService.getCurrentEthDate();
                    if (ethToday) {
                        $scope.ethPicker.year = ethToday.year;
                        $scope.ethPicker.month = ethToday.month;
                    } else {
                        $scope.ethPicker.year = 2019;
                        $scope.ethPicker.month = 2;
                    }
                }
                $scope.buildEthPickerDays();
                $scope.ethPicker.isOpen = true;
            };

            $scope.closeEthPicker = function () {
                $scope.ethPicker.isOpen = false;
                $scope.ethPicker.activeField = null;
            };

            $scope.buildEthPickerDays = function () {
                var year = $scope.ethPicker.year;
                var month = $scope.ethPicker.month;
                var maxDays = month === 13 ? (year % 4 === 3 ? 6 : 5) : 30;

                // Determine start weekday of Ethiopian month
                var mmStr = month < 10 ? '0' + month : '' + month;
                var gregFirst = ethiopianCalendarService.ethToGreg('01/' + mmStr + '/' + year);
                var startWeekday = gregFirst ? gregFirst.getDay() : 0; // 0=Sunday, 6=Saturday

                $scope.ethPicker.leadingBlanks = [];
                for (var b = 0; b < startWeekday; b++) {
                    $scope.ethPicker.leadingBlanks.push(b);
                }

                var days = [];
                for (var d = 1; d <= maxDays; d++) {
                    days.push(d);
                }
                $scope.ethPicker.daysGrid = days;
            };

            $scope.prevEthMonth = function ($event) {
                if ($event) $event.stopPropagation();
                if ($scope.ethPicker.month > 1) {
                    $scope.ethPicker.month--;
                } else {
                    $scope.ethPicker.month = 13;
                    $scope.ethPicker.year--;
                }
                $scope.buildEthPickerDays();
            };

            $scope.nextEthMonth = function ($event) {
                if ($event) $event.stopPropagation();
                if ($scope.ethPicker.month < 13) {
                    $scope.ethPicker.month++;
                } else {
                    $scope.ethPicker.month = 1;
                    $scope.ethPicker.year++;
                }
                $scope.buildEthPickerDays();
            };

            $scope.prevEthYear = function ($event) {
                if ($event) $event.stopPropagation();
                $scope.ethPicker.year--;
                $scope.buildEthPickerDays();
            };

            $scope.nextEthYear = function ($event) {
                if ($event) $event.stopPropagation();
                $scope.ethPicker.year++;
                $scope.buildEthPickerDays();
            };

            $scope.selectEthDay = function (day, $event) {
                if ($event) $event.stopPropagation();
                var dd = day < 10 ? '0' + day : '' + day;
                var mm = $scope.ethPicker.month < 10 ? '0' + $scope.ethPicker.month : '' + $scope.ethPicker.month;
                var val = dd + '/' + mm + '/' + $scope.ethPicker.year;
                if ($scope.ethPicker.activeField) {
                    $scope.filters[$scope.ethPicker.activeField] = val;
                    $scope.filters.dateRangeKey = '';
                    $scope.applyFilters();
                }
                $scope.closeEthPicker();
            };

            $scope.selectEthTodayInPicker = function ($event) {
                if ($event) $event.stopPropagation();
                var ethToday = ethiopianCalendarService.getCurrentEthDate();
                if (ethToday && $scope.ethPicker.activeField) {
                    $scope.filters[$scope.ethPicker.activeField] = ethToday.formatted;
                    $scope.applyFilters();
                }
                $scope.closeEthPicker();
            };

            $scope.clearEthDateInPicker = function ($event) {
                if ($event) $event.stopPropagation();
                if ($scope.ethPicker.activeField) {
                    $scope.filters[$scope.ethPicker.activeField] = '';
                    $scope.applyFilters();
                }
                $scope.closeEthPicker();
            };

            // =========================================================================
            // Switch Active Register Template
            // =========================================================================
            $scope.switchRegister = function (registerId) {
                if ($scope.activeRegister === registerId && $scope.rawRecords.length > 0) return;
                $scope.activeRegister = registerId;

                for (var i = 0; i < $scope.availableRegisters.length; i++) {
                    if ($scope.availableRegisters[i].id === registerId) {
                        $scope.activeRegisterMeta = $scope.availableRegisters[i];
                        break;
                    }
                }

                // Reset filter specifics
                $scope.filters.icuVentilation = '';
                $scope.filters.icuOutcome = '';
                $scope.filters.icuVap = '';
                $scope.filters.icuReadmission = '';
                $scope.filters.visitLocation = '';
                $scope.filters.selectedLocations = [];
                $scope.filters.opdStatus = '';
                $scope.filters.opdRta = '';
                $scope.filters.opdTb = '';
                $scope.filters.opdHiv = '';
                $scope.filters.liaisonType = '';
                $scope.filters.liaisonCaseType = '';
                $scope.filters.liaisonAmbulance = '';
                $scope.filters.liaisonFeedback = '';
                $scope.filters.ipdWard = '';
                $scope.filters.selectedWards = [];
                $scope.filters.ipdStatus = '';
                $scope.multiselectOpen = null;

                // Load Dictionary
                $scope.conceptDictionary = registerService.getRegisterDictionary(registerId);

                // Load Data
                $scope.loadData();
            };

            // =========================================================================
            // Load Data from Server / Service
            // =========================================================================
            $scope.loadData = function () {
                $scope.isLoading = true;
                registerService.fetchRegisterData($scope.activeRegister).then(function (records) {
                    $scope.rawRecords = records;
                    if ($scope.activeRegister === 'OPD') {
                        var locMap = {};
                        for (var k = 0; k < records.length; k++) {
                            if (records[k].visit_location) {
                                locMap[records[k].visit_location] = true;
                            }
                        }
                        $scope.opdLocations = Object.keys(locMap).sort();
                    } else if ($scope.activeRegister === 'IPD') {
                        var wardMap = {};
                        for (var w = 0; w < records.length; w++) {
                            if (records[w].ward_name) {
                                wardMap[records[w].ward_name] = true;
                            }
                        }
                        $scope.ipdWards = Object.keys(wardMap).sort();
                    }

                    if ($scope.filters.dateRangeKey && $scope.filters.dateRangeKey !== 'ALL') {
                        $scope.setDateRange($scope.filters.dateRangeKey);
                    } else {
                        $scope.applyFilters();
                    }
                    $scope.isLoading = false;
                }).catch(function (err) {
                    console.error('Error fetching ' + $scope.activeRegister, err);
                    $scope.isLoading = false;
                });
            };

            // =========================================================================
            // Set Predefined Date Range
            // =========================================================================
            $scope.setDateRange = function (rangeKey) {
                $scope.filters.dateRangeKey = rangeKey;

                if (rangeKey === 'ALL') {
                    $scope.filters.fromEthDate = '';
                    $scope.filters.toEthDate = '';
                } else if (rangeKey === 'TODAY') {
                    var ethToday = ethiopianCalendarService.getCurrentEthDate();
                    $scope.filters.fromEthDate = ethToday ? ethToday.formatted : '';
                    $scope.filters.toEthDate = ethToday ? ethToday.formatted : '';
                } else if (rangeKey === 'MONTH') {
                    var ethNow = ethiopianCalendarService.getCurrentEthDate();
                    $scope.filters.fromEthDate = '01/' + (ethNow.month < 10 ? '0' + ethNow.month : ethNow.month) + '/' + ethNow.year;
                    var maxD = ethNow.month === 13 ? (ethNow.year % 4 === 3 ? 6 : 5) : 30;
                    $scope.filters.toEthDate = maxD + '/' + (ethNow.month < 10 ? '0' + ethNow.month : ethNow.month) + '/' + ethNow.year;
                } else if (rangeKey === 'WEEK') {
                    var pastGreg = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
                    var pastEth = ethiopianCalendarService.gregToEth(pastGreg);
                    var nowEth = ethiopianCalendarService.getCurrentEthDate();
                    $scope.filters.fromEthDate = pastEth ? pastEth.formatted : '';
                    $scope.filters.toEthDate = nowEth ? nowEth.formatted : '';
                }

                $scope.applyFilters();
            };

            // =========================================================================
            // Apply All Filters (Search, Date, Demographics, Register-specific)
            // =========================================================================
            $scope.applyFilters = function () {
                var records = $scope.rawRecords || [];
                var q = ($scope.filters.search || '').trim().toLowerCase();

                // Date Range bounds
                var fromGreg = $scope.filters.fromEthDate ? ethiopianCalendarService.ethToGreg($scope.filters.fromEthDate) : null;
                var toGreg = $scope.filters.toEthDate ? ethiopianCalendarService.ethToGreg($scope.filters.toEthDate) : null;
                if (fromGreg) fromGreg.setHours(0, 0, 0, 0);
                if (toGreg) toGreg.setHours(23, 59, 59, 999);

                $scope.filteredRecords = records.filter(function (row) {
                    // Global Search
                    if (q) {
                        var matchSearch = false;
                        var fieldsToSearch = [
                            row.mrn, row.patient_name, row.visit_location, row.ward_name, row.woreda, row.kebele, row.region,
                            row.admission_diag_name, row.discharge_diag_name, row.diagnosis_name,
                            row.diagnosis, row.facility_name, row.department, row.remark
                        ];
                        for (var i = 0; i < fieldsToSearch.length; i++) {
                            if (fieldsToSearch[i] && String(fieldsToSearch[i]).toLowerCase().indexOf(q) !== -1) {
                                matchSearch = true;
                                break;
                            }
                        }
                        if (!matchSearch) return false;
                    }

                    // Date Filter
                    if (fromGreg || toGreg) {
                        var recDateRaw = row.service_date || row.admission_date || row.referDate;
                        if (recDateRaw) {
                            var recDate = new Date(recDateRaw);
                            if (fromGreg && recDate < fromGreg) return false;
                            if (toGreg && recDate > toGreg) return false;
                        }
                    }

                    // Demographic Filter: Sex
                    if ($scope.filters.sex) {
                        var s = (row.sex || '').toUpperCase();
                        if ($scope.filters.sex === 'M' && s !== 'M' && s !== 'MALE') return false;
                        if ($scope.filters.sex === 'F' && s !== 'F' && s !== 'FEMALE') return false;
                    }

                    // Demographic Filter: Age Group
                    if ($scope.filters.ageGroup) {
                        var a = parseInt(row.age, 10);
                        if (isNaN(a)) a = 0;
                        if ($scope.filters.ageGroup === '<5' && a >= 5) return false;
                        if ($scope.filters.ageGroup === '5-14' && (a < 5 || a > 14)) return false;
                        if ($scope.filters.ageGroup === '15-49' && (a < 15 || a > 49)) return false;
                        if ($scope.filters.ageGroup === '50+' && a < 50) return false;
                    }

                    // ICU Specific Filters
                    if ($scope.activeRegister === 'ICU') {
                        if ($scope.filters.icuVentilation && (row.mech_vent || '').toLowerCase() !== $scope.filters.icuVentilation.toLowerCase()) return false;
                        if ($scope.filters.icuOutcome && (row.outcome_at_discharge || '').toLowerCase().indexOf($scope.filters.icuOutcome.toLowerCase()) === -1) return false;
                        if ($scope.filters.icuVap && (row.vap_developed || '').toLowerCase() !== $scope.filters.icuVap.toLowerCase()) return false;
                        if ($scope.filters.icuReadmission && (row.readmission || '').toLowerCase() !== $scope.filters.icuReadmission.toLowerCase()) return false;
                    }

                    // OPD Specific Filters (with Multiselect Location)
                    if ($scope.activeRegister === 'OPD') {
                        if ($scope.filters.selectedLocations && $scope.filters.selectedLocations.length > 0) {
                            var rowLoc = (row.visit_location || '').toLowerCase();
                            var matchLoc = $scope.filters.selectedLocations.some(function (loc) {
                                return loc.toLowerCase() === rowLoc;
                            });
                            if (!matchLoc) return false;
                        } else if ($scope.filters.visitLocation && (row.visit_location || '') !== $scope.filters.visitLocation) {
                            return false;
                        }

                        if ($scope.filters.opdStatus && (row.patient_status || '').toLowerCase() !== $scope.filters.opdStatus.toLowerCase()) return false;
                        if ($scope.filters.opdRta) {
                            if ($scope.filters.opdRta === 'ANY' && !row.rta_type) return false;
                            if ($scope.filters.opdRta !== 'ANY' && (row.rta_type || '').toLowerCase().indexOf($scope.filters.opdRta.toLowerCase()) === -1) return false;
                        }
                        if ($scope.filters.opdTb) {
                            if ($scope.filters.opdTb === 'Positive' && (row.tb_result || '').toLowerCase() !== 'positive') return false;
                            if ($scope.filters.opdTb === 'Negative' && (row.tb_result || '').toLowerCase() !== 'negative') return false;
                            if ($scope.filters.opdTb === 'Screened' && (row.tb_screened || '').toLowerCase() !== 'yes') return false;
                        }
                        if ($scope.filters.opdHiv) {
                            if ($scope.filters.opdHiv === 'Positive' && (row.hiv_result || '').toLowerCase() !== 'positive') return false;
                            if ($scope.filters.opdHiv === 'Negative' && (row.hiv_result || '').toLowerCase() !== 'negative') return false;
                            if ($scope.filters.opdHiv === 'Tested' && (row.hiv_performed || '').toLowerCase() !== 'yes') return false;
                        }
                    }

                    // Liaison Specific Filters
                    if ($scope.activeRegister === 'LIAISON') {
                        if ($scope.filters.liaisonType && (row.referral_type || '').toLowerCase() !== $scope.filters.liaisonType.toLowerCase()) return false;
                        if ($scope.filters.liaisonCaseType && (row.case_type || '').toLowerCase().indexOf($scope.filters.liaisonCaseType.toLowerCase()) === -1) return false;
                        if ($scope.filters.liaisonAmbulance && (row.ambulance_dispatched || '').toLowerCase() !== $scope.filters.liaisonAmbulance.toLowerCase()) return false;
                        if ($scope.filters.liaisonFeedback) {
                            if ($scope.filters.liaisonFeedback === 'Yes' && (row.feedback_sent_received || '').toLowerCase() !== 'yes') return false;
                            if ($scope.filters.liaisonFeedback === 'Pending' && (row.feedback_sent_received || '').toLowerCase() === 'yes') return false;
                        }
                    }

                    // IPD Specific Filters (with Multiselect Ward)
                    if ($scope.activeRegister === 'IPD') {
                        if ($scope.filters.selectedWards && $scope.filters.selectedWards.length > 0) {
                            var rowWard = (row.ward_name || '').toLowerCase();
                            var matchWard = $scope.filters.selectedWards.some(function (w) {
                                return w.toLowerCase() === rowWard;
                            });
                            if (!matchWard) return false;
                        } else if ($scope.filters.ipdWard && (row.ward_name || '').toLowerCase() !== $scope.filters.ipdWard.toLowerCase()) {
                            return false;
                        }

                        if ($scope.filters.ipdStatus && (row.status || '').toLowerCase() !== $scope.filters.ipdStatus.toLowerCase()) return false;
                    }

                    return true;
                });

                // Re-calculate Dynamic KPIs
                $scope.calculateKPIs();

                // Update Pagination View
                $scope.pagination.currentPage = 1;
                $scope.updatePagination();
            };

            // =========================================================================
            // Dynamic Summary Metric Cards (Recalculated on Active Filters)
            // =========================================================================
            $scope.calculateKPIs = function () {
                var records = $scope.filteredRecords || [];
                var count = records.length;

                if ($scope.activeRegister === 'ICU') {
                    var totalAdmitted = count;
                    var totalDischarged = 0;
                    var onVentilation = 0;
                    var totalStayDays = 0;
                    var inIcuDeaths = 0;

                    for (var i = 0; i < count; i++) {
                        var r = records[i];
                        if (r.status === 'Discharged' || (r.outcome_at_discharge && r.outcome_at_discharge !== 'Active / In ICU')) {
                            totalDischarged++;
                        }
                        if ((r.mech_vent || '').toLowerCase() === 'yes') {
                            onVentilation++;
                        }
                        var los = parseInt(r.length_of_stay, 10);
                        if (!isNaN(los) && los >= 0) {
                            totalStayDays += los;
                        }
                        if ((r.death_in_icu && r.death_in_icu !== 'No') || (r.outcome_at_discharge && r.outcome_at_discharge.indexOf('Died') !== -1)) {
                            inIcuDeaths++;
                        }
                    }

                    var avgStay = count > 0 ? (totalStayDays / count).toFixed(1) : '0.0';

                    $scope.kpis = {
                        card1: { title: 'TOTAL ADMISSIONS', value: totalAdmitted, subtext: (totalAdmitted - totalDischarged) + ' Active | ' + totalDischarged + ' Discharged', icon: 'fa-bed', color: 'stat-blue' },
                        card2: { title: 'MECHANICAL VENTILATION', value: onVentilation, subtext: (count > 0 ? Math.round((onVentilation / count) * 100) : 0) + '% on ventilator support', icon: 'fa-heartbeat', color: 'stat-cyan' },
                        card3: { title: 'AVERAGE LENGTH OF STAY', value: avgStay + ' Days', subtext: totalStayDays + ' Cumulative patient bed days', icon: 'fa-clock-o', color: 'stat-orange' },
                        card4: { title: 'ICU MORTALITY', value: inIcuDeaths, subtext: (count > 0 ? ((inIcuDeaths / count) * 100).toFixed(1) : 0) + '% in-unit death rate', icon: 'fa-user-times', color: inIcuDeaths > 0 ? 'stat-red' : 'stat-green' },
                        card5: { title: 'DISCHARGED / IMPROVED', value: totalDischarged, subtext: (count > 0 ? Math.round((totalDischarged / count) * 100) : 0) + '% discharge rate', icon: 'fa-check-circle', color: 'stat-green' }
                    };
                } else if ($scope.activeRegister === 'OPD') {
                    var newCases = 0;
                    var repeatCases = 0;
                    var rtaCount = 0;
                    var tbScreened = 0;
                    var hivTested = 0;
                    var hivPositive = 0;
                    var referralsOut = 0;

                    for (var j = 0; j < count; j++) {
                        var o = records[j];
                        if (o.isNew || o.patient_status === 'New') newCases++;
                        else repeatCases++;

                        if (o.rta_type) rtaCount++;
                        if ((o.tb_screened || '').toLowerCase() === 'yes' || o.tb_result) tbScreened++;
                        if ((o.hiv_performed || '').toLowerCase() === 'yes') {
                            hivTested++;
                            if ((o.hiv_result || '').toLowerCase() === 'positive') hivPositive++;
                        }
                        if (o.referred_to) referralsOut++;
                    }

                    $scope.kpis = {
                        card1: { title: 'TOTAL OPD VISITS', value: count, subtext: newCases + ' New | ' + repeatCases + ' Repeat', icon: 'fa-users', color: 'stat-blue' },
                        card2: { title: 'TOTAL REFERRALS', value: referralsOut, subtext: 'Referred to other tiers', icon: 'fa-external-link', color: 'stat-cyan' },
                        card3: { title: 'SCREENED FOR TB', value: tbScreened, subtext: (count > 0 ? Math.round((tbScreened / count) * 100) : 0) + '% screening coverage', icon: 'fa-shield', color: 'stat-amber' },
                        card4: { title: 'HIV TESTED / POSITIVE', value: hivTested + ' / ' + hivPositive, subtext: hivPositive + ' reactive cases identified', icon: 'fa-stethoscope', color: 'stat-purple' },
                        card5: { title: 'ROAD TRAFFIC ACCIDENTS', value: rtaCount, subtext: 'Pedestrian, cyclist & vehicle', icon: 'fa-ambulance', color: 'stat-red' }
                    };
                } else if ($scope.activeRegister === 'LIAISON') {
                    var refIn = 0;
                    var refOut = 0;
                    var emergencyCases = 0;
                    var ambDispatched = 0;
                    var feedbackReceived = 0;

                    for (var l = 0; l < count; l++) {
                        var lr = records[l];
                        if (lr.referral_type === 'In' || lr.isReferralIn) refIn++;
                        else refOut++;

                        if (lr.case_type === 'Emergency') emergencyCases++;
                        if (lr.ambulance_dispatched === 'Yes') ambDispatched++;
                        if (lr.feedback_sent_received === 'Yes') feedbackReceived++;
                    }

                    $scope.kpis = {
                        card1: { title: 'TOTAL REFERRAL SERVICES', value: count, subtext: refIn + ' Referral-In | ' + refOut + ' Referral-Out', icon: 'fa-exchange', color: 'stat-blue' },
                        card2: { title: 'REFERRAL INCOMING', value: refIn, subtext: 'From primary facilities / health centers', icon: 'fa-sign-in', color: 'stat-cyan' },
                        card3: { title: 'REFERRAL OUTGOING', value: refOut, subtext: 'Sent to tertiary / specialized centers', icon: 'fa-sign-out', color: 'stat-purple' },
                        card4: { title: 'EMERGENCY TRANSFERS', value: emergencyCases, subtext: ambDispatched + ' Ambulances dispatched', icon: 'fa-ambulance', color: 'stat-red' },
                        card5: { title: 'TWO-WAY FEEDBACK', value: feedbackReceived, subtext: (count > 0 ? Math.round((feedbackReceived / count) * 100) : 0) + '% feedback loop completed', icon: 'fa-check-square-o', color: 'stat-green' }
                    };
                } else if ($scope.activeRegister === 'IPD') {
                    var ipdAdmitted = 0;
                    var ipdDischarged = 0;
                    for (var p = 0; p < count; p++) {
                        if (records[p].status === 'Admitted') ipdAdmitted++;
                        else ipdDischarged++;
                    }
                    $scope.kpis = {
                        card1: { title: 'TOTAL IPD PATIENTS', value: count, subtext: ipdAdmitted + ' Admitted | ' + ipdDischarged + ' Discharged', icon: 'fa-bed', color: 'stat-blue' },
                        card2: { title: 'CURRENTLY ADMITTED', value: ipdAdmitted, subtext: 'Occupying hospital ward beds', icon: 'fa-user-plus', color: 'stat-cyan' },
                        card3: { title: 'DISCHARGED', value: ipdDischarged, subtext: 'Discharged / improved outcomes', icon: 'fa-check-circle', color: 'stat-green' },
                        card4: { title: 'TOTAL WARDS', value: ($scope.ipdWards || []).length, subtext: 'Active inpatient departments', icon: 'fa-hospital-o', color: 'stat-purple' },
                        card5: { title: 'RECORDS VIEW', value: count, subtext: 'Loaded in active view', icon: 'fa-list-alt', color: 'stat-amber' }
                    };
                }
            };

            // =========================================================================
            // Reset Filters
            // =========================================================================
            $scope.resetFilters = function () {
                $scope.filters.search = '';
                $scope.filters.sex = '';
                $scope.filters.ageGroup = '';
                $scope.filters.icuVentilation = '';
                $scope.filters.icuOutcome = '';
                $scope.filters.icuVap = '';
                $scope.filters.icuReadmission = '';
                $scope.filters.visitLocation = '';
                $scope.filters.selectedLocations = [];
                $scope.filters.opdStatus = '';
                $scope.filters.opdRta = '';
                $scope.filters.opdTb = '';
                $scope.filters.opdHiv = '';
                $scope.filters.liaisonType = '';
                $scope.filters.liaisonCaseType = '';
                $scope.filters.liaisonAmbulance = '';
                $scope.filters.liaisonFeedback = '';
                $scope.filters.ipdWard = '';
                $scope.filters.selectedWards = [];
                $scope.filters.ipdStatus = '';
                $scope.multiselectOpen = null;
                $scope.setDateRange('TODAY');
            };

            // =========================================================================
            // Toggle Data Source & Concept Completeness Guide
            // =========================================================================
            $scope.toggleReferenceGuide = function () {
                $scope.isReferenceOpen = !$scope.isReferenceOpen;
            };

            // =========================================================================
            // Export Official Register to Excel (.xls)
            // =========================================================================
            $scope.exportToExcel = function () {
                var tableElement = document.getElementById('moh-register-main-table');
                if (!tableElement) return;

                var title = $scope.activeRegisterMeta.name;
                var ethDate = $scope.currentEthDate;
                var html = '<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">';
                html += '<head><meta charset="utf-8">';
                html += '<style>';
                html += 'table { border-collapse: collapse; font-family: Arial, sans-serif; font-size: 11px; }';
                html += 'th { background-color: #2c3e50; color: #ffffff; border: 1px solid #1a252f; text-align: center; font-weight: bold; }';
                html += 'td { border: 1px solid #cccccc; padding: 4px; text-align: center; }';
                html += '.title-header { font-size: 16px; font-weight: bold; background: #ffffff; color: #000; text-align: center; }';
                html += '</style></head><body>';
                html += '<div class="title-header">' + $scope.facilityName + ' — ' + title + ' (' + ethDate + ' EC)</div><br/>';
                html += tableElement.outerHTML;
                html += '</body></html>';

                var blob = new Blob([html], { type: 'application/vnd.ms-excel;charset=utf-8' });
                var link = document.createElement('a');
                link.href = URL.createObjectURL(blob);
                link.download = $scope.activeRegister + '_Register_' + ($scope.currentEthDate ? $scope.currentEthDate.replace(/\//g, '-') : 'EC') + '.xls';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            };

            // =========================================================================
            // Print MOH Register (A4/A3 Landscape)
            // =========================================================================
            $scope.printRegister = function () {
                $window.print();
            };

            // =========================================================================
            // Global click handler to close datepicker and multiselects when clicking outside
            // =========================================================================
            var docClickHandler = function (e) {
                var target = e.target;
                if ($scope.ethPicker.isOpen) {
                    var dateWrap = document.querySelector('.date-picker-wrap');
                    if (dateWrap && !dateWrap.contains(target)) {
                        $scope.$apply(function () {
                            $scope.closeEthPicker();
                        });
                    }
                }
                if ($scope.multiselectOpen) {
                    var msWraps = document.querySelectorAll('.multiselect-dropdown-wrap');
                    var clickedInside = false;
                    for (var i = 0; i < msWraps.length; i++) {
                        if (msWraps[i].contains(target)) {
                            clickedInside = true;
                            break;
                        }
                    }
                    if (!clickedInside) {
                        $scope.$apply(function () {
                            $scope.closeMultiselect();
                        });
                    }
                }
            };
            document.addEventListener('click', docClickHandler);
            $scope.$on('$destroy', function () {
                document.removeEventListener('click', docClickHandler);
            });

            // =========================================================================
            // Check Authentication & Privilege Access
            // =========================================================================
            function checkAccess() {
                $scope.isAuthChecking = true;
                $http.get('/openmrs/ws/rest/v1/session', { withCredentials: true })
                    .then(function (response) {
                        $scope.isAuthChecking = false;
                        if (!response.data || !response.data.authenticated) {
                            $window.location.href = '../home/index.html#/login';
                            return;
                        }

                        var user = response.data.user || {};
                        $scope.currentUser = user;
                        var privs = (user.privileges || []).map(function (p) { return p.name || p.display; });
                        var roles = (user.roles || []).map(function (r) { return r.name || r.display; });

                        var isSuperUser = roles.indexOf('System Developer') !== -1 ||
                                          roles.indexOf('Super User') !== -1 ||
                                          roles.indexOf('SuperAdmin') !== -1 ||
                                          roles.indexOf('Privilege Level: Full') !== -1;

                        var hasPrivilege = isSuperUser ||
                                          privs.indexOf('app:register') !== -1 ||
                                          roles.indexOf('Register-App') !== -1;

                        if (hasPrivilege) {
                            $scope.isAuthorized = true;
                            $scope.switchRegister('ICU');
                        } else {
                            $scope.isAuthorized = false;
                            $scope.accessError = 'Access Denied: You do not have permission to access the Register application. Required privilege: "app:register".';
                        }
                    })
                    .catch(function (error) {
                        console.warn('Could not verify session with OpenMRS, allowing local fallback:', error);
                        $scope.isAuthChecking = false;
                        $scope.isAuthorized = true;
                        $scope.switchRegister('ICU');
                    });
            }

            // Initialize Access Check
            checkAccess();
        }
    ]);
