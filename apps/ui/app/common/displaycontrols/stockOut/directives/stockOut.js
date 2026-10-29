"use strict";

angular.module('bahmni.common.displaycontrol.stockOut')
    .directive('stockOut', ['$http', '$q', 'spinner', '$rootScope', '$stateParams',
        function ($http, $q, spinner, $rootScope, $stateParams) {
            var controller = function ($scope) {
                $scope.patientStockOutOrders = [];
                $scope.facilityStockOutTests = [];
                $scope.activeView = 'patient';
                $scope.loading = true;
                $scope.hasData = false;

                var getPatientUuid = function () {
                    return $scope.patientUuid ||
                           ($scope.patient && $scope.patient.uuid) ||
                           ($stateParams && $stateParams.patientUuid) ||
                           ($rootScope && $rootScope.patient && $rootScope.patient.uuid) ||
                           ($scope.$parent && $scope.$parent.patient && $scope.$parent.patient.uuid) ||
                           ($scope.$parent && $scope.$parent.$parent && $scope.$parent.$parent.patient && $scope.$parent.$parent.patient.uuid) ||
                           null;
                };

                var isStockOutReason = function (reason) {
                    if (!reason || typeof reason !== 'string') return false;
                    var lower = reason.toLowerCase();
                    return lower.indexOf('stock') !== -1 ||
                           lower.indexOf('reagent') !== -1 ||
                           lower.indexOf('unavailable') !== -1;
                };

                var getLocalStockOutTests = function () {
                    var list = [];
                    try {
                        var cached = localStorage.getItem('stockOutTests') || localStorage.getItem('stockStatus');
                        if (cached) {
                            var parsed = JSON.parse(cached);
                            if (Array.isArray(parsed)) {
                                parsed.forEach(function (item) {
                                    if (typeof item === 'string') {
                                        list.push({ name: item, reason: 'Reagent Stock Out', status: 'Stock-Out' });
                                    } else if (item && (item.name || item.testName)) {
                                        list.push({
                                            name: item.testName || item.name,
                                            section: item.sampleType || item.section || 'Laboratory',
                                            reason: item.reason || 'Reagent Stock Out',
                                            status: 'Stock-Out'
                                        });
                                    }
                                });
                            } else if (parsed && typeof parsed === 'object') {
                                Object.keys(parsed).forEach(function (key) {
                                    if (key && parsed[key] === true && key !== 'error') {
                                        list.push({
                                            name: key,
                                            section: 'Laboratory',
                                            reason: 'Reagent Stock Out',
                                            status: 'Stock-Out'
                                        });
                                    }
                                });
                            }
                        }
                    } catch (e) {}
                    return list;
                };

                var loadPatientOrders = function () {
                    var pUuid = getPatientUuid();
                    if (!pUuid) return $q.when([]);

                    var ordersPromise = $http.get('/openmrs/ws/rest/v1/order', {
                        params: {
                            patient: pUuid,
                            v: 'custom:(uuid,orderNumber,concept:(uuid,name:(display),display),action,dateActivated,dateStopped,voided,voidReason,commentToFulfiller,orderType:(name))'
                        }
                    }).then(function (res) {
                        return (res.data && res.data.results) ? res.data.results : [];
                    }).catch(function () {
                        return [];
                    });

                    var obsPromise = $http.get('/openmrs/ws/rest/v1/obs', {
                        params: {
                            patient: pUuid,
                            v: 'custom:(uuid,obsDatetime,value,comment,concept:(uuid,name:(display),display))'
                        }
                    }).then(function (res) {
                        return (res.data && res.data.results) ? res.data.results : [];
                    }).catch(function () {
                        return [];
                    });

                    return $q.all([ordersPromise, obsPromise]).then(function (results) {
                        var orders = results[0];
                        var obsList = results[1];
                        var stockOutList = [];
                        var seenMap = {};

                        // Process stock-out observations
                        obsList.forEach(function (ob) {
                            var val = ob.value || '';
                            if (typeof val === 'string' && (val.indexOf('[STOCK-OUT') !== -1 || val.indexOf('[Stock-Out') !== -1)) {
                                var match = val.match(/\[STOCK-OUT:[^\]]*\]\s*(.*)/i) || val.match(/\[STOCK-OUT\]\s*(.*)/i);
                                var testName = match ? match[1].trim() : val.trim();
                                var key = (testName || '').toLowerCase() + '_' + (ob.obsDatetime || '').substr(0, 10);
                                if (!seenMap[key]) {
                                    seenMap[key] = true;
                                    stockOutList.push({
                                        uuid: ob.uuid,
                                        orderNumber: '',
                                        testName: testName || 'Laboratory Test',
                                        orderDate: ob.obsDatetime,
                                        voidReason: 'Reagent Stock Out',
                                        voided: false,
                                        status: 'Stock-Out'
                                    });
                                }
                            }
                        });

                        // Process any stock-out orders
                        var localMap = {};
                        getLocalStockOutTests().forEach(function (t) {
                            if (t.name) localMap[t.name.toLowerCase().trim()] = true;
                        });

                        orders.forEach(function (o) {
                            var testName = '';
                            if (o.concept) {
                                if (o.concept.display) testName = o.concept.display;
                                else if (o.concept.name && o.concept.name.display) testName = o.concept.name.display;
                                else if (o.concept.name) testName = o.concept.name;
                            }
                            var lowerName = (testName || '').toLowerCase().trim();
                            var inCatalog = false;
                            if (lowerName) {
                                if (localMap[lowerName]) {
                                    inCatalog = true;
                                } else {
                                    for (var k in localMap) {
                                        if (k && (lowerName.indexOf(k) !== -1 || k.indexOf(lowerName) !== -1)) {
                                            inCatalog = true;
                                            break;
                                        }
                                    }
                                }
                            }

                            var comment = o.commentToFulfiller || '';
                            var voidReason = o.voidReason || '';
                            var isStockOut = isStockOutReason(voidReason) ||
                                             isStockOutReason(comment) ||
                                             inCatalog;

                            if (isStockOut) {
                                var displayReason = 'Reagent Stock Out';
                                if (comment && isStockOutReason(comment)) {
                                    displayReason = comment.replace(/\[LAB_LOCATION:[^\]]*\]\s*/g, '').trim();
                                } else if (voidReason && isStockOutReason(voidReason)) {
                                    displayReason = voidReason;
                                }

                                var ordDate = o.dateActivated || o.dateStopped;
                                var key = lowerName + '_' + (ordDate || '').substr(0, 10);
                                if (!seenMap[key]) {
                                    seenMap[key] = true;
                                    stockOutList.push({
                                        uuid: o.uuid,
                                        orderNumber: o.orderNumber,
                                        testName: testName || 'Laboratory Test',
                                        orderDate: ordDate,
                                        voidReason: displayReason || 'Reagent Stock Out',
                                        voided: o.voided,
                                        status: 'Stock-Out'
                                    });
                                }
                            }
                        });

                        stockOutList.sort(function (a, b) {
                            var da = new Date(a.orderDate || 0);
                            var db = new Date(b.orderDate || 0);
                            return db - da;
                        });

                        return stockOutList;
                    }).catch(function () {
                        return [];
                    });
                };

                var init = function () {
                    var p = $http.get('/openelis/pages/test/inactiveTests.jsp').then(function (res) {
                        if (res.data && typeof res.data === 'object') {
                            try {
                                localStorage.setItem('stockOutTests', JSON.stringify(res.data));
                            } catch (e) {}
                        }
                    }).catch(function () {}).finally(function () {
                        $scope.facilityStockOutTests = getLocalStockOutTests();
                        return loadPatientOrders().then(function (stockOutList) {
                            $scope.patientStockOutOrders = stockOutList;
                            $scope.hasData = ($scope.patientStockOutOrders.length > 0) || ($scope.facilityStockOutTests.length > 0);
                            if ($scope.patientStockOutOrders.length > 0) {
                                $scope.activeView = 'patient';
                            } else if ($scope.facilityStockOutTests.length > 0) {
                                $scope.activeView = 'facility';
                            } else {
                                $scope.activeView = 'patient';
                            }
                            $scope.loading = false;
                        });
                    });
                    spinner.forPromise(p);
                };

                $scope.switchView = function (v) {
                    $scope.activeView = v;
                };

                $scope.printStockOutNotice = function (item) {
                    var items = item ? [item] : ($scope.activeView === 'patient' ? $scope.patientStockOutOrders : $scope.facilityStockOutTests);
                    if (!items || items.length === 0) return;

                    var patientName = 'Patient';
                    var patientId = '';
                    var patient = $scope.patient || ($rootScope && $rootScope.patient);
                    if (patient) {
                        patientName = patient.name || ((patient.givenName || '') + ' ' + (patient.familyName || '')).trim() || 'Patient';
                        patientId = patient.identifier || '';
                    }

                    var user = $rootScope.currentUser;
                    var clinicianName = user ? (user.provider ? (user.provider.display || user.provider.name || '') : user.username) : '';

                    var now = new Date();
                    var dateStr = now.toLocaleDateString() + ' ' + now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                    var noticeNo = 'SO-' + now.getFullYear() + ('0' + (now.getMonth() + 1)).slice(-2) + ('0' + now.getDate()).slice(-2) + '-' + Math.floor(1000 + Math.random() * 9000);

                    var printWin = window.open('', '_blank', 'width=800,height=700');
                    if (!printWin) {
                        alert("Please allow popups to print notice.");
                        return;
                    }

                    var html = '<!DOCTYPE html><html><head><meta charset="utf-8">';
                    html += '<title>Stock-Out Notice - Boru Meda Hospital</title>';
                    html += '<style>';
                    html += 'body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;margin:30px;font-size:13px;color:#222;}';
                    html += '.header{text-align:center;border-bottom:2px solid #2c3e50;padding-bottom:12px;margin-bottom:16px;}';
                    html += '.header h1{margin:0;font-size:18px;color:#1e3a8a;text-transform:uppercase;}';
                    html += '.header h2{margin:4px 0 0 0;font-size:14px;color:#dc2626;}';
                    html += '.meta-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px 16px;margin:16px 0;background:#f8fafc;border:1px solid #e2e8f0;padding:12px;border-radius:4px;}';
                    html += '.meta-item{display:flex;gap:8px;font-size:12px;}';
                    html += '.meta-label{font-weight:bold;color:#475569;min-width:110px;}';
                    html += 'table{width:100%;border-collapse:collapse;margin:16px 0;}';
                    html += 'th,td{border:1px solid #cbd5e1;padding:8px 10px;font-size:12px;text-align:left;}';
                    html += 'th{background:#f1f5f9;color:#1e293b;font-weight:bold;}';
                    html += '.badge-so{background:#fee2e2;color:#b91c1c;font-weight:bold;padding:2px 6px;border-radius:3px;font-size:11px;}';
                    html += '.notice-box{border:1px solid #f87171;background:#fff1f2;border-radius:4px;padding:12px;margin:16px 0;}';
                    html += '.sig-grid{display:grid;grid-template-columns:1fr 1fr;gap:40px;margin-top:50px;}';
                    html += '.sig-box{border-top:1px solid #000;padding-top:6px;text-align:center;font-size:11px;}';
                    html += '.footer{text-align:center;font-size:10px;color:#64748b;margin-top:30px;border-top:1px dashed #cbd5e1;padding-top:8px;}';
                    html += '@media print{.no-print{display:none;}}';
                    html += '</style></head><body>';

                    html += '<div class="header">';
                    html += '<h1>Boru Meda General Hospital</h1>';
                    html += '<div style="font-size:12px;color:#475569;">Laboratory & Diagnostic Services Department</div>';
                    html += '<h2>LABORATORY REAGENT STOCK-OUT NOTICE</h2>';
                    html += '</div>';

                    html += '<div class="meta-grid">';
                    html += '<div class="meta-item"><span class="meta-label">Notice Ref:</span><span>' + noticeNo + '</span></div>';
                    html += '<div class="meta-item"><span class="meta-label">Date:</span><span>' + dateStr + '</span></div>';
                    html += '<div class="meta-item"><span class="meta-label">Patient Name:</span><span>' + patientName + '</span></div>';
                    html += '<div class="meta-item"><span class="meta-label">MRN / ID:</span><span>' + (patientId || 'N/A') + '</span></div>';
                    if (clinicianName) {
                        html += '<div class="meta-item"><span class="meta-label">Clinician:</span><span>' + clinicianName + '</span></div>';
                    }
                    html += '</div>';

                    html += '<h3>Stock-Out Test(s)</h3>';
                    html += '<table><thead><tr><th>#</th><th>Test Name</th><th>Category / Reason</th><th>Status</th></tr></thead><tbody>';
                    items.forEach(function (it, idx) {
                        html += '<tr><td>' + (idx + 1) + '</td><td><strong>' + (it.testName || it.name) + '</strong></td><td>' + (it.voidReason || it.reason || 'Reagent Stock Out') + '</td><td><span class="badge-so">STOCK-OUT</span></td></tr>';
                    });
                    html += '</tbody></table>';

                    html += '<div class="notice-box"><strong>Notice to Patient & Clinician:</strong><br>The test(s) listed above could not be performed due to reagent unavailability in Boru Meda Hospital. Please consult with the attending physician for alternative diagnostic modalities or external referral.</div>';

                    html += '<div class="sig-grid">';
                    html += '<div class="sig-box"><strong>Clinician / Laboratory Officer</strong><br>Signature & Stamp</div>';
                    html += '<div class="sig-box"><strong>Patient / Guardian</strong><br>Signature</div>';
                    html += '</div>';

                    html += '<div class="footer">Boru Meda General Hospital &bull; Generated on ' + dateStr + '</div>';
                    html += '<div class="no-print" style="margin-top:20px;text-align:center;"><button onclick="window.print()" style="padding:8px 18px;background:#1e3a8a;color:#fff;border:none;border-radius:4px;cursor:pointer;font-weight:bold;">Print Notice</button></div>';
                    html += '</body></html>';

                    printWin.document.open();
                    printWin.document.write(html);
                    printWin.document.close();
                    setTimeout(function () { printWin.print(); }, 400);
                };

                $scope.$watch('patientUuid', function (newUuid) {
                    if (newUuid && (!$scope.patientStockOutOrders || $scope.patientStockOutOrders.length === 0)) {
                        init();
                    }
                });
                $scope.$watch('patient', function (newP) {
                    if (newP && newP.uuid && (!$scope.patientStockOutOrders || $scope.patientStockOutOrders.length === 0)) {
                        init();
                    }
                });

                init();
            };

            return {
                restrict: 'E',
                controller: controller,
                templateUrl: "../common/displaycontrols/stockOut/views/stockOut.html",
                scope: {
                    params: "=",
                    patient: "=?",
                    patientUuid: "=?"
                }
            };
        }]);
