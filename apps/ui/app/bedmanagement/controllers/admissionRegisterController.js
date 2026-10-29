'use strict';

angular.module('bahmni.ipd')
    .controller('AdmissionRegisterController', ['$scope', '$http', '$state', '$rootScope', 'spinner', '$bahmniCookieStore', '$filter', '$injector', 'wardService',
        function ($scope, $http, $state, $rootScope, spinner, $bahmniCookieStore, $filter, $injector, wardService) {
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

            $scope.admissions = [];
            $scope.filteredAdmissions = [];
            $scope.paginatedAdmissions = [];
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
            $scope.wardList = [];

            // Branding
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
            }).catch(function () {});

            // Fetch wards list for ward filter dropdown
            wardService.getWardsList().then(function (res) {
                if (res.data && res.data.results) {
                    $scope.wardList = res.data.results.map(function (w) {
                        return w.ward && w.ward.name ? w.ward.name : '';
                    }).filter(Boolean);
                }
            }).catch(function () {});

            $scope.searchParams = {
                query: '',
                status: '',
                ward: '',
                dateFrom: null,
                dateTo: null
            };

            $scope.sortField = 'admission_date';
            $scope.sortReverse = true;

            $scope.sortBy = function (field) {
                if ($scope.sortField === field) {
                    $scope.sortReverse = !$scope.sortReverse;
                } else {
                    $scope.sortField = field;
                    $scope.sortReverse = false;
                }
                $scope.applyFilters();
            };

            $scope.loadAdmissions = function (forceSpinner) {
                $scope.isLoading = true;
                var params = {
                    q: 'emrapi.sqlSearch.admissionRegister',
                    v: 'full'
                };
                var req = $http.get(Bahmni.Common.Constants.sqlUrl, {
                    params: params
                }).then(function (response) {
                    $scope.admissions = response.data || [];
                    $rootScope.cachedAdmissions = $scope.admissions;
                    $scope.applyFilters();
                    $scope.isLoading = false;
                }).catch(function (error) {
                    console.error('Error loading admission register:', error);
                    $scope.isLoading = false;
                });

                if (forceSpinner || (!$scope.admissions || $scope.admissions.length === 0)) {
                    spinner.forPromise(req);
                }
            };

            $scope.applyFilters = function () {
                var results = angular.copy($scope.admissions);
                var f = $scope.searchParams;

                if (f.query) {
                    var qLower = f.query.toLowerCase().trim();
                    results = results.filter(function (r) {
                        return (r.patient_name && r.patient_name.toLowerCase().indexOf(qLower) !== -1) ||
                               (r.mrn && r.mrn.toLowerCase().indexOf(qLower) !== -1) ||
                               (r.bed_number && r.bed_number.toLowerCase().indexOf(qLower) !== -1) ||
                               (r.admission_diagnosis && r.admission_diagnosis.toLowerCase().indexOf(qLower) !== -1) ||
                               (r.icd11_code && r.icd11_code.toLowerCase().indexOf(qLower) !== -1);
                    });
                }

                if (f.status) {
                    results = results.filter(function (r) {
                        return r.status === f.status;
                    });
                }

                if (f.ward) {
                    results = results.filter(function (r) {
                        return r.ward_name === f.ward;
                    });
                }

                if (f.dateFrom) {
                    var df = parseDateValue(f.dateFrom);
                    if (df) {
                        df.setHours(0, 0, 0, 0);
                        results = results.filter(function (r) {
                            if (!r.admission_date) return false;
                            var ad = new Date(r.admission_date);
                            return ad >= df;
                        });
                    }
                }

                if (f.dateTo) {
                    var dt = parseDateValue(f.dateTo);
                    if (dt) {
                        dt.setHours(23, 59, 59, 999);
                        results = results.filter(function (r) {
                            if (!r.admission_date) return false;
                            var ad = new Date(r.admission_date);
                            return ad <= dt;
                        });
                    }
                }

                // Sorting
                results.sort(function (a, b) {
                    var valA = a[$scope.sortField] || '';
                    var valB = b[$scope.sortField] || '';
                    if (valA < valB) return $scope.sortReverse ? 1 : -1;
                    if (valA > valB) return $scope.sortReverse ? -1 : 1;
                    return 0;
                });

                $scope.filteredAdmissions = results;
                $scope.currentPage = 1;
                $scope.updatePagination();
            };

            $scope.resetFilters = function () {
                $scope.searchParams = {
                    query: '',
                    status: '',
                    ward: '',
                    dateFrom: null,
                    dateTo: null
                };
                $scope.applyFilters();
            };

            $scope.updatePagination = function () {
                var total = $scope.filteredAdmissions.length;
                if ($scope.pageSize === 'All') {
                    $scope.totalPages = 1;
                    $scope.startItem = total > 0 ? 1 : 0;
                    $scope.endItem = total;
                    $scope.paginatedAdmissions = $scope.filteredAdmissions;
                } else {
                    var sz = parseInt($scope.pageSize, 10);
                    $scope.totalPages = Math.ceil(total / sz) || 1;
                    if ($scope.currentPage > $scope.totalPages) {
                        $scope.currentPage = $scope.totalPages;
                    }
                    var start = ($scope.currentPage - 1) * sz;
                    var end = Math.min(start + sz, total);
                    $scope.startItem = total > 0 ? start + 1 : 0;
                    $scope.endItem = end;
                    $scope.paginatedAdmissions = $scope.filteredAdmissions.slice(start, end);
                }
            };

            $scope.setPage = function (p) {
                if (p >= 1 && p <= $scope.totalPages) {
                    $scope.currentPage = p;
                    $scope.updatePagination();
                }
            };

            $scope.getAdmissionEthDate = function (r) {
                if (!r || !r.admission_date) return '';
                return toEthiopianDate(r.admission_date);
            };

            $scope.getDischargeEthDate = function (r) {
                if (!r || !r.discharge_date) return '-';
                return toEthiopianDate(r.discharge_date);
            };

            $scope.goToPatient = function (r) {
                if (!r || !r.patient_uuid) return;
                var url = '../clinical/#/default/patient/' + r.patient_uuid + '/dashboard';
                window.open(url, '_blank');
            };

            $scope.printRegister = function () {
                $scope.isPrintingRegister = true;
                setTimeout(function () {
                    window.print();
                    $scope.$apply(function () {
                        $scope.isPrintingRegister = false;
                    });
                }, 150);
            };

            $scope.exportToExcel = function () {
                var dataToExport = $scope.filteredAdmissions;
                if (!dataToExport || dataToExport.length === 0) {
                    alert('No admission records to export with the current filters.');
                    return;
                }

                var nowEth = toEthiopianDate(new Date());
                var nowGreg = new Date().toISOString().slice(0, 10);
                var fileName = 'MOH_Admission_Discharge_Register_' + nowGreg + '.xls';

                var escapeXml = function (str) {
                    if (str === null || str === undefined) return '';
                    return String(str)
                        .replace(/&/g, '&amp;')
                        .replace(/</g, '&lt;')
                        .replace(/>/g, '&gt;')
                        .replace(/"/g, '&quot;')
                        .replace(/'/g, '&apos;');
                };

                var xml = '<?xml version="1.0" encoding="UTF-8"?>\r\n' +
                    '<?mso-application progid="Excel.Sheet"?>\r\n' +
                    '<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"\r\n' +
                    ' xmlns:o="urn:schemas-microsoft-com:office:office"\r\n' +
                    ' xmlns:x="urn:schemas-microsoft-com:office:excel"\r\n' +
                    ' xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet"\r\n' +
                    ' xmlns:html="http://www.w3.org/TR/REC-html40">\r\n' +
                    '<Styles>\r\n' +
                    ' <Style ss:ID="Default" ss:Name="Normal">\r\n' +
                    '  <Alignment ss:Vertical="Center"/>\r\n' +
                    '  <Font ss:FontName="Segoe UI" ss:Size="9"/>\r\n' +
                    ' </Style>\r\n' +
                    ' <Style ss:ID="Title">\r\n' +
                    '  <Alignment ss:Horizontal="Center" ss:Vertical="Center"/>\r\n' +
                    '  <Font ss:FontName="Segoe UI" ss:Size="14" ss:Bold="1" ss:Color="#003366"/>\r\n' +
                    ' </Style>\r\n' +
                    ' <Style ss:ID="SubTitle">\r\n' +
                    '  <Alignment ss:Horizontal="Center" ss:Vertical="Center"/>\r\n' +
                    '  <Font ss:FontName="Segoe UI" ss:Size="10" ss:Italic="1" ss:Color="#333333"/>\r\n' +
                    ' </Style>\r\n' +
                    ' <Style ss:ID="GroupHeader">\r\n' +
                    '  <Alignment ss:Horizontal="Center" ss:Vertical="Center" ss:WrapText="1"/>\r\n' +
                    '  <Borders>\r\n' +
                    '   <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1"/>\r\n' +
                    '   <Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1"/>\r\n' +
                    '   <Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1"/>\r\n' +
                    '   <Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1"/>\r\n' +
                    '  </Borders>\r\n' +
                    '  <Font ss:FontName="Segoe UI" ss:Size="9" ss:Bold="1" ss:Color="#002D62"/>\r\n' +
                    '  <Interior ss:Color="#D9E1F2" ss:Pattern="Solid"/>\r\n' +
                    ' </Style>\r\n' +
                    ' <Style ss:ID="ColHeader">\r\n' +
                    '  <Alignment ss:Horizontal="Center" ss:Vertical="Center" ss:WrapText="1"/>\r\n' +
                    '  <Borders>\r\n' +
                    '   <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1"/>\r\n' +
                    '   <Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1"/>\r\n' +
                    '   <Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1"/>\r\n' +
                    '   <Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1"/>\r\n' +
                    '  </Borders>\r\n' +
                    '  <Font ss:FontName="Segoe UI" ss:Size="8" ss:Bold="1" ss:Color="#000000"/>\r\n' +
                    '  <Interior ss:Color="#F2F2F2" ss:Pattern="Solid"/>\r\n' +
                    ' </Style>\r\n' +
                    ' <Style ss:ID="DataCell">\r\n' +
                    '  <Alignment ss:Vertical="Center" ss:WrapText="1"/>\r\n' +
                    '  <Borders>\r\n' +
                    '   <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#DDDDDD"/>\r\n' +
                    '   <Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#DDDDDD"/>\r\n' +
                    '   <Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#DDDDDD"/>\r\n' +
                    '   <Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#DDDDDD"/>\r\n' +
                    '  </Borders>\r\n' +
                    '  <Font ss:FontName="Segoe UI" ss:Size="9"/>\r\n' +
                    ' </Style>\r\n' +
                    ' <Style ss:ID="DataCellCenter">\r\n' +
                    '  <Alignment ss:Horizontal="Center" ss:Vertical="Center"/>\r\n' +
                    '  <Borders>\r\n' +
                    '   <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#DDDDDD"/>\r\n' +
                    '   <Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#DDDDDD"/>\r\n' +
                    '   <Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#DDDDDD"/>\r\n' +
                    '   <Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#DDDDDD"/>\r\n' +
                    '  </Borders>\r\n' +
                    '  <Font ss:FontName="Segoe UI" ss:Size="9"/>\r\n' +
                    ' </Style>\r\n' +
                    '</Styles>\r\n' +
                    '<Worksheet ss:Name="Admission Discharge Register">\r\n' +
                    '<Table>\r\n';

                // Column Widths (28 columns total)
                var colWidths = [35, 75, 120, 35, 45, 90, 85, 140, 60, 75, 50, 50, 60, 50, 55, 50, 50, 60, 65, 80, 55, 60, 130, 65, 65, 70, 70, 70, 90];
                for (var w = 0; w < colWidths.length; w++) {
                    xml += '<Column ss:Width="' + colWidths[w] + '"/>\r\n';
                }

                // Row 1: Title
                xml += '<Row ss:Height="28">\r\n';
                xml += '<Cell ss:MergeAcross="28" ss:StyleID="Title"><Data ss:Type="String">FEDERAL DEMOCRATIC REPUBLIC OF ETHIOPIA - MINISTRY OF HEALTH</Data></Cell>\r\n';
                xml += '</Row>\r\n';

                // Row 2: Subtitle
                xml += '<Row ss:Height="22">\r\n';
                xml += '<Cell ss:MergeAcross="28" ss:StyleID="SubTitle"><Data ss:Type="String">Admission / Discharge Register | Facility: ' + escapeXml($scope.facilityName) + ' | Ward: ' + escapeXml($scope.searchParams.ward || 'All Wards') + ' | Date: ' + escapeXml(nowEth) + ' E.C.</Data></Cell>\r\n';
                xml += '</Row>\r\n';

                // Row 3: Blank separator
                xml += '<Row ss:Height="10"></Row>\r\n';

                // Row 4: Group Headers
                xml += '<Row ss:Height="24">\r\n';
                xml += '<Cell ss:StyleID="GroupHeader"><Data ss:Type="String"></Data></Cell>\r\n'; // S/No
                xml += '<Cell ss:MergeAcross="4" ss:StyleID="GroupHeader"><Data ss:Type="String">Identification</Data></Cell>\r\n';
                xml += '<Cell ss:MergeAcross="3" ss:StyleID="GroupHeader"><Data ss:Type="String">Admission</Data></Cell>\r\n';
                xml += '<Cell ss:MergeAcross="3" ss:StyleID="GroupHeader"><Data ss:Type="String">Provider initiated testing &amp; counseling (PITC)</Data></Cell>\r\n';
                xml += '<Cell ss:StyleID="GroupHeader"><Data ss:Type="String">Malaria</Data></Cell>\r\n';
                xml += '<Cell ss:MergeAcross="3" ss:StyleID="GroupHeader"><Data ss:Type="String">TB screening</Data></Cell>\r\n';
                xml += '<Cell ss:MergeAcross="3" ss:StyleID="GroupHeader"><Data ss:Type="String">Discharge</Data></Cell>\r\n';
                xml += '<Cell ss:StyleID="GroupHeader"><Data ss:Type="String">Death in IPD</Data></Cell>\r\n';
                xml += '<Cell ss:StyleID="GroupHeader"><Data ss:Type="String">Death Notif.</Data></Cell>\r\n';
                xml += '<Cell ss:MergeAcross="2" ss:StyleID="GroupHeader"><Data ss:Type="String">Finance</Data></Cell>\r\n';
                xml += '<Cell ss:MergeAcross="1" ss:StyleID="GroupHeader"><Data ss:Type="String">Remark</Data></Cell>\r\n';
                xml += '</Row>\r\n';

                // Row 5: Column Headers
                xml += '<Row ss:Height="32">\r\n';
                var headers = [
                    'S/No (1)', 'MRN (2)', 'Patient Name', 'Age (3)', 'Sex (4)', 'Woreda/Subcity (5)',
                    'Date of Admission (6)', 'ESV_ICD11 Diagnosis (7)', 'ICD Code', 'Road Traffic Accident (8)',
                    'HIV Test Offered (9)', 'HIV Test Performed (10)', 'Target Pop (11)', 'HIV Test Result (12)',
                    'Travel Malarious (13)', 'Screened for TB (14)', 'TB Result (15)', 'Diag Eval Code (16)', 'TB Screen Result (17)',
                    'Date of Discharge (18)', 'LOS Days (19)', 'Condition Code (20)', 'Discharge Diagnosis (21)',
                    'Death in IPD (22)', 'Death Notif Given (23)', 'Amount Charged (24)', 'Amount Paid (25)', 'Voucher No (26)', 'Ward / Bed & Remark (27)'
                ];
                for (var h = 0; h < headers.length; h++) {
                    xml += '<Cell ss:StyleID="ColHeader"><Data ss:Type="String">' + escapeXml(headers[h]) + '</Data></Cell>\r\n';
                }
                xml += '</Row>\r\n';

                // Data Rows
                for (var i = 0; i < dataToExport.length; i++) {
                    var item = dataToExport[i];
                    var admEth = toEthiopianDate(item.admission_date);
                    var disEth = toEthiopianDate(item.discharge_date);

                    xml += '<Row ss:Height="22">\r\n';
                    xml += '<Cell ss:StyleID="DataCellCenter"><Data ss:Type="Number">' + (i + 1) + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCellCenter"><Data ss:Type="String">' + escapeXml(item.mrn) + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCell"><Data ss:Type="String">' + escapeXml(item.patient_name) + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCellCenter"><Data ss:Type="String">' + escapeXml(item.age) + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCellCenter"><Data ss:Type="String">' + escapeXml(item.sex) + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCell"><Data ss:Type="String">' + escapeXml(item.woreda) + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCellCenter"><Data ss:Type="String">' + escapeXml(admEth) + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCell"><Data ss:Type="String">' + escapeXml(item.admission_diagnosis) + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCellCenter"><Data ss:Type="String">' + escapeXml(item.icd11_code) + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCellCenter"><Data ss:Type="String">' + escapeXml(item.road_traffic_accident) + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCellCenter"><Data ss:Type="String">' + escapeXml(item.hiv_offered) + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCellCenter"><Data ss:Type="String">' + escapeXml(item.hiv_performed) + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCellCenter"><Data ss:Type="String">' + escapeXml(item.hiv_target_category) + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCellCenter"><Data ss:Type="String">' + escapeXml(item.hiv_result) + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCellCenter"><Data ss:Type="String">' + escapeXml(item.travel_malaria) + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCellCenter"><Data ss:Type="String">' + escapeXml(item.tb_screened) + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCellCenter"><Data ss:Type="String">' + escapeXml(item.tb_result) + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCellCenter"><Data ss:Type="String">' + escapeXml(item.tb_eval_type) + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCellCenter"><Data ss:Type="String">' + escapeXml(item.tb_screening_result) + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCellCenter"><Data ss:Type="String">' + escapeXml(disEth || '-') + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCellCenter"><Data ss:Type="String">' + escapeXml(item.length_of_stay) + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCell"><Data ss:Type="String">' + escapeXml(item.condition_at_discharge) + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCell"><Data ss:Type="String">' + escapeXml(item.discharge_diagnosis) + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCellCenter"><Data ss:Type="String">' + escapeXml(item.death_in_ipd) + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCellCenter"><Data ss:Type="String">' + escapeXml(item.death_notification) + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCellCenter"><Data ss:Type="String">-</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCellCenter"><Data ss:Type="String">' + escapeXml(item.payment_method) + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCellCenter"><Data ss:Type="String">' + escapeXml(item.voucher_no) + '</Data></Cell>\r\n';
                    xml += '<Cell ss:StyleID="DataCell"><Data ss:Type="String">' + escapeXml(item.ward_name + ' / Bed ' + item.bed_number) + '</Data></Cell>\r\n';
                    xml += '</Row>\r\n';
                }

                xml += '</Table>\r\n</Worksheet>\r\n</Workbook>';

                var blob = new Blob([xml], { type: 'application/vnd.ms-excel;charset=utf-8;' });
                var link = document.createElement('a');
                var url = URL.createObjectURL(blob);
                link.setAttribute('href', url);
                link.setAttribute('download', fileName);
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            };

            // ==========================================
            // DATA SOURCE & CONCEPT REFERENCE DICTIONARY
            // (To follow and audit data completeness)
            // ==========================================
            $scope.isReferenceOpen = false;
            $scope.selectedRefCategory = 'All';
            $scope.referenceSearchText = '';
            $scope.highlightedColNumber = null;
            $scope.activeColumnDetail = null;

            $scope.referenceCategories = [
                'All',
                'Identification',
                'Admission',
                'PITC',
                'Malaria',
                'TB Screening',
                'Discharge',
                'Death in IPD',
                'Finance'
            ];

            $scope.columnReferenceList = [
                {
                    colNumber: 1,
                    name: "Serial Number (S/No)",
                    mohHeader: "S/No (1)",
                    category: "Identification",
                    formName: "System Auto-Sequence",
                    tabName: "Admission Register",
                    conceptName: "Sequential Row Index",
                    conceptId: "N/A (System)",
                    dbField: "(Page - 1) * PageSize + Index + 1",
                    dataType: "Integer",
                    completenessTarget: "100% Mandatory",
                    auditRule: "Sequential numbered index for each inpatient admitted within the reporting period.",
                    howToComplete: "Automatically numbered sequentially by Bahmni in the register table form."
                },
                {
                    colNumber: 2,
                    name: "Medical Record Number (MRN)",
                    mohHeader: "MRN (2)",
                    category: "Identification",
                    formName: "Registration Details Form",
                    tabName: "Registration Module",
                    conceptName: "Patient Identifier (Primary Identifier Type)",
                    conceptId: "bahmni.primaryIdentifierType",
                    dbField: "patient_identifier.identifier",
                    dataType: "String (Hospital ID)",
                    completenessTarget: "100% Mandatory",
                    auditRule: "Unique hospital registration number generated at patient intake. Must never be blank.",
                    howToComplete: "Generated automatically or assigned in Registration module during patient intake."
                },
                {
                    colNumber: 3,
                    name: "Full Name of Patient",
                    mohHeader: "Patient Name (3)",
                    category: "Identification",
                    formName: "Registration Details Form",
                    tabName: "Registration Module > Demographics",
                    conceptName: "Person Name (Given, Middle, Family Name)",
                    conceptId: "person_name",
                    dbField: "person_name.given_name + middle_name + family_name",
                    dataType: "Text",
                    completenessTarget: "100% Mandatory (3 parts)",
                    auditRule: "Must contain Patient Name, Father Name, and Grandfather Name in Ethiopian naming convention.",
                    howToComplete: "Enter complete 3-part name in Registration Demographics tab."
                },
                {
                    colNumber: 4,
                    name: "Age",
                    mohHeader: "Age (3)",
                    category: "Identification",
                    formName: "Registration Details Form",
                    tabName: "Registration Module > Demographics",
                    conceptName: "Birthdate / Estimated Age",
                    conceptId: "person.birthdate",
                    dbField: "TIMESTAMPDIFF(YEAR, person.birthdate, visit.date_started)",
                    dataType: "Integer (Years)",
                    completenessTarget: "100% Mandatory",
                    auditRule: "Must reflect accurate patient age at the time of admission. Critical for pediatric and geriatric indicators.",
                    howToComplete: "Record date of birth or estimated age in Registration. Bahmni computes exact age at admission."
                },
                {
                    colNumber: 5,
                    name: "Sex / Gender",
                    mohHeader: "Sex (4)",
                    category: "Identification",
                    formName: "Registration Details Form",
                    tabName: "Registration Module > Demographics",
                    conceptName: "Gender",
                    conceptId: "person.gender",
                    dbField: "person.gender ('M' / 'F')",
                    dataType: "Coded ('M', 'F')",
                    completenessTarget: "100% Mandatory",
                    auditRule: "Mandatory biological sex selection. Required for reproductive health & disaggregated HMIS reporting.",
                    howToComplete: "Select Male or Female in Registration Demographics."
                },
                {
                    colNumber: 6,
                    name: "Address: Woreda / Kebele",
                    mohHeader: "Woreda / Kebele (5)",
                    category: "Identification",
                    formName: "Registration Details Form > Address Hierarchy",
                    tabName: "Registration Module > Address",
                    conceptName: "City / Village / Kebele (Address Hierarchy Level 3/4)",
                    conceptId: "person_address.city_village",
                    dbField: "person_address.city_village / address1",
                    dataType: "Text",
                    completenessTarget: "100% Mandatory",
                    auditRule: "Patient's permanent residential Woreda or Kebele. Required for catchment area and referral analysis.",
                    howToComplete: "Select from Address Hierarchy dropdown in Registration or type residential Woreda / Kebele."
                },
                {
                    colNumber: 7,
                    name: "Address: Sub city / Zone / House No",
                    mohHeader: "Sub city / Zone (5)",
                    category: "Identification",
                    formName: "Registration Details Form > Address Hierarchy",
                    tabName: "Registration Module > Address",
                    conceptName: "Subcity / Zone (Address Hierarchy Level 2)",
                    conceptId: "person_address.address2",
                    dbField: "person_address.address2 / state_province",
                    dataType: "Text",
                    completenessTarget: "Expected for urban residents",
                    auditRule: "Specific Zone, Subcity, Got, or Ketena. Facilitates contact tracing and community follow-up.",
                    howToComplete: "Fill Subcity or Zone in Registration Address section."
                },
                {
                    colNumber: 8,
                    name: "Date of Admission",
                    mohHeader: "Date of Admission (6)",
                    category: "Admission",
                    formName: "Bed Management (ADT) > Admit Patient",
                    tabName: "Bed Management / Inpatient Visit",
                    conceptName: "Visit Start Date (Ethiopian Calendar E.C.)",
                    conceptId: "visit.date_started",
                    dbField: "visit.date_started (Rendered in DD/MM/YYYY E.C.)",
                    dataType: "Date",
                    completenessTarget: "100% Mandatory",
                    auditRule: "Exact admission timestamp converted to Ethiopian Calendar. Crucial for bed occupancy and length of stay.",
                    howToComplete: "Initiated when patient is admitted in ADT / Bed Management or assigned to an inpatient ward visit."
                },
                {
                    colNumber: 9,
                    name: "Admission Ward & Bed Number",
                    mohHeader: "Ward / Bed & Remark (27)",
                    category: "Admission",
                    formName: "Bed Management > Ward Grid View",
                    tabName: "Bed Management Module",
                    conceptName: "Bed Patient Assignment Map",
                    conceptId: "bed_patient_assignment_map",
                    dbField: "visit_type.name (Ward) + bed.bed_number",
                    dataType: "Text",
                    completenessTarget: "100% Mandatory for admitted patients",
                    auditRule: "Every active inpatient must be mapped to an official physical ward and bed number.",
                    howToComplete: "Go to Bed Management tab, select the patient, and click an available bed in their ward to assign."
                },
                {
                    colNumber: 10,
                    name: "ESV_ICD11 Diagnosis Name at Admission",
                    mohHeader: "ESV_ICD11 Diagnosis Name (7)",
                    category: "Admission",
                    formName: "Clinical Consultation > Diagnosis Tab OR Admission Letter Form",
                    tabName: "Clinical Consultation > Diagnosis",
                    conceptName: "Coded Diagnosis / Visit Diagnoses",
                    conceptId: "22 (Coded Diagnosis) / 20 (Visit Diagnoses)",
                    dbField: "obs.value_coded -> concept_name.name",
                    dataType: "Coded Concept",
                    completenessTarget: "100% Mandatory within 24h",
                    auditRule: "Provisional or working clinical diagnosis documented by attending physician upon ward admission.",
                    howToComplete: "In Clinical Consultation, click 'Diagnosis' tab, search the disease name, select Primary, and save."
                },
                {
                    colNumber: 11,
                    name: "ICD-11 Diagnosis Code",
                    mohHeader: "Code (7)",
                    category: "Admission",
                    formName: "Clinical Consultation > Diagnosis Tab",
                    tabName: "Clinical Consultation > Diagnosis",
                    conceptName: "Concept Reference Term (ICD-11 / ICD-10)",
                    conceptId: "concept_reference_term.code",
                    dbField: "concept_reference_term.code",
                    dataType: "String Code (e.g. 1B10, BA00)",
                    completenessTarget: "100% Mandatory for all coded diagnoses",
                    auditRule: "Standardized international classification code corresponding to the admission diagnosis.",
                    howToComplete: "Mapped automatically when selecting a standardized coded diagnosis in the Diagnosis tab."
                },
                {
                    colNumber: 12,
                    name: "Road Traffic Accident (RTA)",
                    mohHeader: "Road Traffic Accident (8)",
                    category: "Admission",
                    formName: "Emergency / History and Examination Form",
                    tabName: "Clinical Consultation > Observations",
                    conceptName: "Road traffic accident",
                    conceptId: "3325 / 11924",
                    dbField: "obs.value_coded / obs.value_text",
                    dataType: "Coded (1=Pedestrian, 2=Motorcyclist, 3=Vehicle occupant)",
                    completenessTarget: "Mandatory for all trauma admissions",
                    auditRule: "Classifies road injury mechanism: 1. Pedestrian, 2. Motorcyclist, 3. Vehicle occupant.",
                    howToComplete: "In Clinical Consultation > Observations, open Emergency / History Form and record RTA category."
                },
                {
                    colNumber: 13,
                    name: "PITC: HIV Test Offered",
                    mohHeader: "HIV Offered (9)",
                    category: "PITC",
                    formName: "PITC Screening Form / History and Examination",
                    tabName: "Clinical Consultation > Observations",
                    conceptName: "HIV test offered",
                    conceptId: "63657",
                    dbField: "obs.value_coded (Yes / No)",
                    dataType: "Coded (Yes / No)",
                    completenessTarget: "100% Mandatory for all IPD admissions",
                    auditRule: "Ethiopian National Guideline requires provider-initiated HIV testing offer for every inpatient.",
                    howToComplete: "In Clinical Consultation > Observations, open PITC Screening and select 'Yes' for HIV Test Offered."
                },
                {
                    colNumber: 14,
                    name: "PITC: HIV Test Performed",
                    mohHeader: "HIV Performed (10)",
                    category: "PITC",
                    formName: "PITC Screening Form / Rapid Testing Observation",
                    tabName: "Clinical Consultation > Observations",
                    conceptName: "HIV test performed",
                    conceptId: "22442 / 63658",
                    dbField: "obs.value_coded (Yes / No)",
                    dataType: "Coded (Yes / No)",
                    completenessTarget: "Required if HIV Test was accepted",
                    auditRule: "Indicates whether rapid antibody screening was actually carried out during this hospitalization.",
                    howToComplete: "Record 'Yes' in PITC Screening form once test is administered by nurse or lab technician."
                },
                {
                    colNumber: 15,
                    name: "PITC: Target Population Category",
                    mohHeader: "Target Pop Code (11)",
                    category: "PITC",
                    formName: "PITC Screening Form",
                    tabName: "Clinical Consultation > Observations",
                    conceptName: "HIV Target Population Category",
                    conceptId: "PITC Target Category",
                    dbField: "obs.value_coded / obs.value_text",
                    dataType: "Coded Code",
                    completenessTarget: "Required for tested patients",
                    auditRule: "Categorizes target group: General population, Key population, Malnourished child, TB patient, Pregnant.",
                    howToComplete: "Select the corresponding target population group code in the PITC Screening form."
                },
                {
                    colNumber: 16,
                    name: "PITC: HIV Test Result",
                    mohHeader: "HIV Result (12)",
                    category: "PITC",
                    formName: "PITC Screening Form / HIV Status Observation",
                    tabName: "Clinical Consultation > Observations / Lab",
                    conceptName: "HIV Status",
                    conceptId: "32992 / 47297",
                    dbField: "obs.value_coded (Positive, Negative, Previously Known Positive)",
                    dataType: "Coded (P / N / KP)",
                    completenessTarget: "100% of tested patients must have result",
                    auditRule: "Confirms HIV serostatus: P (Reactive/Positive) or N (Non-Reactive/Negative). Triggers ART linkage.",
                    howToComplete: "Record rapid test result in PITC Screening or Lab Module. Reactive cases prompt immediate ART consult."
                },
                {
                    colNumber: 17,
                    name: "Malaria: Travel History to Malarious Area",
                    mohHeader: "Travel History to malarious area (13)",
                    category: "Malaria",
                    formName: "Malaria Form (Form ID: 10) / History & Examination",
                    tabName: "Clinical Consultation > Observations",
                    conceptName: "Travel History to Malaria Endemic Area",
                    conceptId: "Malaria Travel History",
                    dbField: "obs.value_coded (Yes / No)",
                    dataType: "Coded (Yes / No)",
                    completenessTarget: "Mandatory for febrile admissions",
                    auditRule: "Identifies if patient visited a known malaria-endemic locality within the past 2 to 4 weeks.",
                    howToComplete: "In Clinical Consultation > Observations, open the Malaria Form and record travel history."
                },
                {
                    colNumber: 18,
                    name: "TB Screening: Screened for TB",
                    mohHeader: "TB Screened (14)",
                    category: "TB Screening",
                    formName: "TB Screening Form / History and Examination",
                    tabName: "Clinical Consultation > Observations",
                    conceptName: "Screened for TB",
                    conceptId: "63266",
                    dbField: "obs.value_coded (Yes / No)",
                    dataType: "Coded (Yes / No)",
                    completenessTarget: "100% Mandatory for all IPD admissions",
                    auditRule: "National requirement to evaluate all inpatients using the 4-symptom TB screening tool.",
                    howToComplete: "In Clinical Consultation > Observations, open TB Screening and evaluate cough, fever, night sweats, weight loss."
                },
                {
                    colNumber: 19,
                    name: "TB Screening: Screening Result",
                    mohHeader: "TB Result (15)",
                    category: "TB Screening",
                    formName: "TB Screening Form",
                    tabName: "Clinical Consultation > Observations",
                    conceptName: "TB screening result",
                    conceptId: "63267",
                    dbField: "obs.value_coded (Presumptive TB / Screen Negative)",
                    dataType: "Coded (P / N)",
                    completenessTarget: "100% of screened patients",
                    auditRule: "P = Presumptive TB (any symptom positive, requires GeneXpert); N = Negative (no symptoms).",
                    howToComplete: "Record 'Presumptive' or 'Negative' based on symptom evaluation in TB Screening form."
                },
                {
                    colNumber: 20,
                    name: "TB Screening: Diagnostic Evaluation Type",
                    mohHeader: "Diag Eval Code (16)",
                    category: "TB Screening",
                    formName: "Lab Orders / Radiology Orders",
                    tabName: "Clinical Consultation > Orders Tab",
                    conceptName: "TB Diagnostic Test Ordered",
                    conceptId: "Lab/Radiology Orders",
                    dbField: "orders.order_id (1=GeneXpert, 2=Smear, 3=Chest X-Ray)",
                    dataType: "Coded Code (1, 2, 3)",
                    completenessTarget: "100% Mandatory for Presumptive TB",
                    auditRule: "Records investigation type ordered for presumptive cases: 1. GeneXpert MTB/RIF, 2. Smear, 3. Chest X-Ray.",
                    howToComplete: "Order GeneXpert or Chest X-Ray in Orders module for every patient marked Presumptive TB."
                },
                {
                    colNumber: 21,
                    name: "TB Diagnostic Confirmation Result",
                    mohHeader: "TB Screen Result (17)",
                    category: "TB Screening",
                    formName: "Lab Results / TB Screening Form",
                    tabName: "Clinical Consultation > Observations / Lab",
                    conceptName: "TB Confirmation Diagnosis",
                    conceptId: "TB Diagnosis Result",
                    dbField: "obs.value_coded (TB Confirmed / No TB / Not Done)",
                    dataType: "Coded (TB / No TB / ND)",
                    completenessTarget: "Mandatory for presumptive cases",
                    auditRule: "Documents laboratory confirmation: Confirmed TB (link to DOTS), No TB, or Not Done (ND).",
                    howToComplete: "Record GeneXpert laboratory result in Lab module or update TB screening summary."
                },
                {
                    colNumber: 22,
                    name: "Date of Discharge",
                    mohHeader: "Date of Discharge (18)",
                    category: "Discharge",
                    formName: "Bed Management (ADT) > Discharge Action",
                    tabName: "Bed Management / ADT Module",
                    conceptName: "Visit Stop Date (Ethiopian Calendar E.C.)",
                    conceptId: "visit.date_stopped",
                    dbField: "visit.date_stopped (Rendered in DD/MM/YYYY E.C.)",
                    dataType: "Date",
                    completenessTarget: "100% Mandatory when patient departs ward",
                    auditRule: "Official discharge timestamp. Must not be null for discharged patients. Converted to Ethiopian Calendar.",
                    howToComplete: "In Bed Management tab, click patient and click 'Discharge' when physician confirms discharge."
                },
                {
                    colNumber: 23,
                    name: "Length of Stay (LOS in Days)",
                    mohHeader: "LOS (days) (19)",
                    category: "Discharge",
                    formName: "System Calculated (Stay Duration)",
                    tabName: "Bed Management / Admission Register",
                    conceptName: "Length of Inpatient Stay",
                    conceptId: "Calculated (date_stopped - date_started)",
                    dbField: "DATEDIFF(IFNULL(v.date_stopped, NOW()), v.date_started)",
                    dataType: "Integer (Days)",
                    completenessTarget: "100% Automatically Computed",
                    auditRule: "Total calendar days between admission and discharge. Key hospital bed utilization metric.",
                    howToComplete: "Computed automatically by comparing admission date with discharge date."
                },
                {
                    colNumber: 24,
                    name: "Condition at Discharge",
                    mohHeader: "Condition at Discharge (20)",
                    category: "Discharge",
                    formName: "Clinical Consultation > Disposition Tab OR Discharge Note",
                    tabName: "Clinical Consultation > Disposition",
                    conceptName: "Discharge Disposition / Condition at Discharge",
                    conceptId: "Discharge Disposition",
                    dbField: "obs.value_coded / disposition",
                    dataType: "Coded (1=Improved, 2=Same, 3=Deteriorated, 4=Absconded)",
                    completenessTarget: "100% Mandatory for all discharges",
                    auditRule: "Outcome status: 1. Improved, 2. Same, 3. Deteriorated, 4. Absconded, 5. Died, 6. Transferred.",
                    howToComplete: "In Clinical Consultation > Disposition tab, select the discharge outcome before discharging."
                },
                {
                    colNumber: 25,
                    name: "ESV_ICD11 Diagnosis at Discharge",
                    mohHeader: "ESV_ICD11 Diagnosis at discharge (21)",
                    category: "Discharge",
                    formName: "Clinical Consultation > Diagnosis Tab (Discharge)",
                    tabName: "Clinical Consultation > Diagnosis",
                    conceptName: "Coded Diagnosis (Discharge / Final)",
                    conceptId: "22 (Coded Diagnosis)",
                    dbField: "obs.value_coded -> concept_name.name",
                    dataType: "Coded Concept",
                    completenessTarget: "100% Mandatory at discharge",
                    auditRule: "Final confirmed diagnosis established by attending physician after clinical investigations.",
                    howToComplete: "In Diagnosis tab, add final confirmed diagnosis and mark certainty as 'CONFIRMED'."
                },
                {
                    colNumber: 26,
                    name: "Death in IPD & Death Notification",
                    mohHeader: "Death in IPD (22) & Death Notif. (23)",
                    category: "Death in IPD",
                    formName: "Death Note (Form ID: 2) & ADT Discharge",
                    tabName: "Clinical Consultation > Observations / ADT",
                    conceptName: "Patient Died / Death Certificate",
                    conceptId: "person.dead, person.death_date, Death Note",
                    dbField: "person.dead=1, TIMESTAMPDIFF(HOUR, v.date_started, death_date) <= 24",
                    dataType: "Coded (1: <=24h, 2: >24h; Notif: Y/N)",
                    completenessTarget: "100% Mandatory for in-hospital deaths",
                    auditRule: "Mortality audit: distinguishes early death (<=24 hrs of admission) vs late death (>24 hrs). Death notification must be documented.",
                    howToComplete: "Fill Death Note form with exact time of death and mark disposition as 'Died' in ADT."
                },
                {
                    colNumber: 27,
                    name: "Finance: Payment Method & Voucher No / Remark",
                    mohHeader: "Amount (24/25), Voucher (26), Remark (27)",
                    category: "Finance",
                    formName: "Registration Details > Payment Attributes",
                    tabName: "Registration Module > Payment",
                    conceptName: "Payment Category & CBHI Voucher",
                    conceptId: "Person Attribute Type 17 (Payment) & 15 (Voucher)",
                    dbField: "person_attribute.value",
                    dataType: "Text / Attribute",
                    completenessTarget: "100% Mandatory",
                    auditRule: "Billing classification: CBHI (Community-Based Health Insurance), Paying, Free/Exempted, Credit.",
                    howToComplete: "In Registration, select Payment Scheme (CBHI, Paying, Free) and enter voucher/card number."
                }
            ];

            $scope.toggleReferenceGuide = function (colNumber) {
                $scope.isReferenceOpen = !$scope.isReferenceOpen;
                if (colNumber) {
                    $scope.highlightedColNumber = colNumber;
                }
            };

            $scope.showColumnInfo = function (colNumber, event) {
                if (event) event.stopPropagation();
                var col = $scope.columnReferenceList.find(function (c) { return c.colNumber === colNumber; });
                if (col) {
                    $scope.activeColumnDetail = col;
                    $scope.highlightedColNumber = colNumber;
                    $scope.isReferenceOpen = true;
                }
            };

            $scope.closeColumnDetail = function () {
                $scope.activeColumnDetail = null;
            };

            $scope.setRefCategory = function (cat) {
                $scope.selectedRefCategory = cat;
            };

            $scope.filterReferenceList = function (item) {
                if ($scope.selectedRefCategory !== 'All' && item.category !== $scope.selectedRefCategory) {
                    return false;
                }
                if ($scope.referenceSearchText) {
                    var q = $scope.referenceSearchText.toLowerCase();
                    return (item.name && item.name.toLowerCase().indexOf(q) !== -1) ||
                           (item.formName && item.formName.toLowerCase().indexOf(q) !== -1) ||
                           (item.conceptName && item.conceptName.toLowerCase().indexOf(q) !== -1) ||
                           (item.conceptId && ('' + item.conceptId).toLowerCase().indexOf(q) !== -1) ||
                           (item.category && item.category.toLowerCase().indexOf(q) !== -1) ||
                           (item.auditRule && item.auditRule.toLowerCase().indexOf(q) !== -1) ||
                           (item.howToComplete && item.howToComplete.toLowerCase().indexOf(q) !== -1);
                }
                return true;
            };

            // Fast cache hydration
            if ($rootScope.cachedAdmissions && $rootScope.cachedAdmissions.length > 0) {
                $scope.admissions = $rootScope.cachedAdmissions;
                $scope.applyFilters();
            }

            $scope.loadAdmissions();
        }
    ]);
