'use strict';

angular.module('bahmni.clinical')
    .controller('OrderController', ['$scope', '$rootScope', '$state', 'allOrderables', 'ngDialog', 'diagnosisService', 'retrospectiveEntryService', 'appService', '$translate', 'LogicAndConditionConfigsLoader', '$http', '$interval',
        function ($scope, $rootScope, $state, allOrderables, ngDialog, diagnosisService, retrospectiveEntryService, appService, $translate, LogicAndConditionConfigsLoader, $http, $interval) {
            $scope.consultation.orders = $scope.consultation.orders || [];
            $scope.consultation.childOrders = $scope.consultation.childOrders || [];
            $scope.consultation.referralOrders = $scope.consultation.referralOrders || [];
            $scope.referralOrders = $scope.consultation.referralOrders;
            $scope.isReferralOrderPresent = function (test) {
                if (!test || !$scope.referralOrders) return false;
                return _.some($scope.referralOrders, function (r) {
                    return r.uuid === test.uuid || (r.concept && r.concept.uuid === test.uuid);
                });
            };
            $scope.openelisInactiveTests = {};

            var fetchInactiveTests = function () {
                return $http.get('/openelis/pages/test/inactiveTests.jsp').then(function (response) {
                    if (response.data && typeof response.data === 'object') {
                        $scope.openelisInactiveTests = response.data;
                        try {
                            localStorage.setItem('stockOutTests', JSON.stringify(response.data));
                        } catch (e) {}
                    }
                }).catch(function (err) {
                    console.warn('Failed to load inactive tests from OpenELIS', err);
                });
            };
            fetchInactiveTests();

            var inactivePoll = $interval(fetchInactiveTests, 15000);
            $scope.$on('$destroy', function () {
                if (inactivePoll) $interval.cancel(inactivePoll);
            });

            $scope.allOrdersTemplates = allOrderables;
            var RadiologyOrderOptionsConfig = appService.getAppDescriptor().getConfig("enableRadiologyOrderOptions");
            var LabOrderOptionsConfig = appService.getAppDescriptor().getConfig("enableLabOrderOptions");
            $scope.enableRadiologyOrderOptions = RadiologyOrderOptionsConfig ? RadiologyOrderOptionsConfig.value : null;
            $scope.enableLabOrderOptions = LabOrderOptionsConfig ? LabOrderOptionsConfig.value : null;
            var testConceptToParentsMapping = {};
            $scope.hideLabTests = true;
            var orderableTests = [];
            const STORAGE_KEY = 'ACTIONS_AND_ANNOTATIONS';
            $scope.configs = [];
            const nameValueSet = new Set(JSON.parse(localStorage.getItem(STORAGE_KEY)) || []);
            const nameValueArray = Array.from(nameValueSet);

            $scope.labLocations = [];
            $scope.locationData = { selectedLabLocation: null };

            var fetchLabLocations = function () {
                var url = '/openelis/pages/location/labLocationList.jsp';
                return $http.get(url).catch(function () {
                    return $http.get('/openelis/LabLocationList.do');
                }).then(function (response) {
                    if (response && response.data && response.data.locations) {
                        $scope.labLocations = response.data.locations;
                    }
                }).catch(function (err) {
                    console.error('Failed to load lab locations', err);
                });
            };

            var restoreLabLocation = function () {
                var savedId = localStorage.getItem('selectedLabLocationId');
                if (savedId && $scope.labLocations.length > 0) {
                    var exists = $scope.labLocations.some(function (l) { return l.id === parseInt(savedId); });
                    if (exists) {
                        $scope.locationData.selectedLabLocation = parseInt(savedId);
                        $scope.consultation.labLocationId = $scope.locationData.selectedLabLocation;
                        $scope.consultation.labLocationName = localStorage.getItem('selectedLabLocationName');
                    }
                }
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

            fetchLabLocations().then(restoreLabLocation);

            $scope.orderableTestsAvailability = function () {
                LogicAndConditionConfigsLoader.loadOrderSelecterConfigs()
                    .then(function (configs) {
                        if (configs) {
                            $scope.configs = configs;
                            let matching = false;
                            let orderables

                            nameValueArray.forEach(key => {
                                $scope.configs.forEach(item => {
                                    if (item.value === key[item.case]) {
                                        matching = true;
                                        orderables = item.orderables;
                                    }
                                });
                            });

                            if (matching) {
                                orderableTests = [...orderableTests, ...orderables];
                            } else {
                                orderableTests.length = 0;
                            }

                        }
                    })
                    .catch(function (error) {
                        console.error('Error loading validation Configs:', error);
                    });
            };

            $scope.orderableTestsAvailability();

            var collapseExistingActiveSection = function (section) {
                if (section) {
                    section.klass = "";
                }
            };

            $scope.toggleLabTests = function () {
                $scope.hideLabTests = !$scope.hideLabTests;
            };

            var showFirstLeftCategoryByDefault = function () {
                if (!$scope.activeTab.leftCategory) {
                    var allLeftCategories = $scope.getOrderTemplate($scope.activeTab.name).setMembers;
                    if (allLeftCategories.length > 0) {
                        $scope.showLeftCategoryTests(allLeftCategories[0]);
                    }
                }
            };

            var findTest = function (testUuid) {
                var test;
                var allLeftCategories = $scope.getOrderTemplate($scope.activeTab.name).setMembers;
                _.each(allLeftCategories, function (leftCategory) {
                    var foundTest = _.find(leftCategory.setMembers, function (test) {
                        return test.uuid === testUuid;
                    });
                    if (foundTest) {
                        test = foundTest;
                        return;
                    }
                });
                return test;
            };

            var removeOrder = function (testUuid) {
                var order = _.find($scope.consultation.orders, function (order) {
                    return order.concept.uuid === testUuid;
                });
                if (order) {
                    if (order.uuid) {
                        order.isDiscontinued = true;
                        $state.orderRemoved = true;
                    } else {
                        _.remove($scope.consultation.orders, order);
                    }
                }
            };

            var createOrder = function (test) {
                var discontinuedOrder = _.find($scope.consultation.orders, function (order) {
                    return (test.uuid === order.concept.uuid) && order.isDiscontinued;
                });
                if (discontinuedOrder) {
                    discontinuedOrder.isDiscontinued = false;
                } else {
                    var activeTabName = $scope.activeTab ? $scope.activeTab.name : null;
                    var createdOrder = Bahmni.Clinical.Order.create(test, activeTabName);
                    $scope.consultation.orders.push(createdOrder);
                    $state.orderCreated = true;
                    if (test.automatic !== undefined) {
                        $scope.consultation.orders.forEach(order => {
                            order.automatic = true;
                        })
                    }
                }
            };

            var initTestConceptToParentsMapping = function () {
                var allLeftCategories = $scope.getOrderTemplate($scope.activeTab.name).setMembers;
                _.each(allLeftCategories, function (leftCategory) {
                    _.each(leftCategory.setMembers, function (member) {
                        if (member.setMembers.length !== 0) {
                            _.each(member.setMembers, function (child) {
                                if (testConceptToParentsMapping[child.uuid] === undefined) {
                                    testConceptToParentsMapping[child.uuid] = [];
                                }
                                testConceptToParentsMapping[child.uuid].push(member.uuid);
                            });
                        }
                    });
                });
            };

            var init = function () {
                $scope.tabs = [];
                _.forEach($scope.allOrdersTemplates, function (item) {
                    var conceptName = $scope.getName(item);
                    var tabName = conceptName || item.name.name;
                    var key = '\'' + tabName + '\'';
                    $scope.allOrdersTemplates[key] = $scope.filterOrderTemplateByClassMap(item);
                    $scope.tabs.push({name: tabName, topLevelConcept: item.name.name});
                });
                if ($scope.tabs) {
                    $scope.activateTab($scope.tabs[0]);
                    initTestConceptToParentsMapping();
                }
            };

            $scope.isRetrospectiveMode = function () {
                return !_.isEmpty(retrospectiveEntryService.getRetrospectiveEntry());
            };

            $scope.activateTab = function (tab) {
                fetchInactiveTests();
                if (tab.klass === "active") {
                    tab.klass = "";
                    $scope.activeTab = undefined;
                } else {
                    collapseExistingActiveSection($scope.activeTab);
                    $scope.activeTab = tab;
                    $scope.activeTab.klass = "active";
                    $scope.activeFilterCategory = null;
                    $scope.updateSelectedOrdersForActiveTab();
                    initTestConceptToParentsMapping();
                    showFirstLeftCategoryByDefault();
                    buildAllCategories();
                }
            };

            $scope.updateSelectedOrdersForActiveTab = function () {
                if (!$scope.activeTab) {
                    return;
                }
                var activeTabTestConcepts = _.map(_.flatten(_.map($scope.getOrderTemplate($scope.activeTab.name).setMembers, 'setMembers')), 'uuid');
                $scope.selectedOrders = _.filter($scope.consultation.orders, function (testOrder) {
                    var inTab = _.indexOf(activeTabTestConcepts, testOrder.concept.uuid) !== -1;
                    return inTab && !$scope.isTestUnavailable(testOrder.concept || testOrder);
                });

                if ($scope.consultation && $scope.consultation.orders) {
                    $scope.consultation.orders.forEach(function (order) {
                        if (order && !order.isDiscontinued && $scope.isTestUnavailable(order.concept || order)) {
                            var ordUuid = order.concept ? order.concept.uuid : order.uuid;
                            var exists = _.some($scope.referralOrders, function (r) {
                                return r.uuid === ordUuid || (r.concept && r.concept.uuid === ordUuid);
                            });
                            if (!exists) {
                                var resolvedName = $scope.getName(order.concept) || extractTestName(order.concept) || (order.concept ? (order.concept.displayName || order.concept.name) : 'Test');
                                $scope.referralOrders.push({
                                    uuid: ordUuid,
                                    name: resolvedName,
                                    displayName: resolvedName,
                                    concept: order.concept || order,
                                    sample: order.concept || order,
                                    isUnavailable: true
                                });
                            }
                        }
                    });
                }

                _.each($scope.selectedOrders, function (order) {
                    order.isUrgent = order.urgency == "STAT" ? true : order.isUrgent;
                });
            };

            $scope.$on('$stateChangeStart', function () {
                if ($state.orderRemoved || $state.orderCreated) {
                    $state.dirtyConsultationForm = true;
                }
            });

            $scope.getOrderTemplate = function (templateName) {
                var key = '\'' + templateName + '\'';
                return $scope.allOrdersTemplates[key];
            };

            $scope.filterOrderTemplateByClassMap = function (orderTemplate) {
                var orderTypeClassMapConfig = appService.getAppDescriptor().getConfig("orderTypeClassMap");
                var orderTypeClassMap = orderTypeClassMapConfig ? orderTypeClassMapConfig.value : {};
                var orderTypeName = $scope.getNameInDefaultLocale(orderTemplate);

                if (orderTypeClassMap[orderTypeName]) {
                    var orderClasses = orderTypeClassMap[orderTypeName];
                    var filteredOrderTemplate = angular.copy(orderTemplate);

                    filteredOrderTemplate.setMembers = filteredOrderTemplate.setMembers
                        .map(function (category) {
                            category.setMembers = category.setMembers.filter(function (test) {
                                return orderClasses.includes(test.conceptClass.name);
                            });
                            return category;
                        });

                    return filteredOrderTemplate;
                }

                return orderTemplate;
            };

            $scope.showLeftCategoryTests = function (leftCategory) {
                collapseExistingActiveSection($scope.activeTab.leftCategory);
                $scope.activeTab.leftCategory = leftCategory;
                $scope.activeTab.leftCategory.klass = "active";
                $scope.activeTab.leftCategory.groups = $scope.getConceptClassesInSet(leftCategory);
            };

            $scope.getConceptClassesInSet = function (conceptSet) {
                var conceptsWithUniqueClass = _.uniqBy(conceptSet ? conceptSet.setMembers : [], function (concept) { return concept.conceptClass.uuid; });
                var conceptClasses = [];
                _.forEach(conceptsWithUniqueClass, function (concept) {
                    conceptClasses.push({name: concept.conceptClass.name, description: concept.conceptClass.description});
                });
                conceptClasses = _.sortBy(conceptClasses, 'name');
                return conceptClasses;
            };

            $scope.$watchCollection('consultation.orders', $scope.updateSelectedOrdersForActiveTab);

            $scope.handleOrderClick = function (order) {
                var test = findTest(order.concept.uuid);
                $scope.toggleOrderSelection(test);
            };

            $scope.search = {};
            $scope.search.string = '';
            $scope.advancedFilterVisible = false;
            $scope.activeFilterCategory = null;
            $scope.activeTypeFilter = 'panels';
            $scope.allCategories = [];

            $scope.resetSearchString = function () {
                $scope.search.string = '';
            };

            $scope.filterByConceptClass = function (test) {
                if (!$scope.activeTab || !$scope.activeTab.leftCategory || !$scope.activeTab.leftCategory.groups) return false;
                var groupNames = $scope.activeTab.leftCategory.groups.map(function (g) { return g.name; });
                if (groupNames.indexOf(test.conceptClass.name) === -1) return false;
                if ($scope.activeFilterCategory && test.conceptClass.name !== $scope.activeFilterCategory) return false;
                if ($scope.matchesTypeFilter && !$scope.matchesTypeFilter(test)) return false;
                return true;
            };

            $scope.filterBySearchString = function (test) {
                if (!$scope.search.string) return true;
                var searchLower = _.toLower($scope.search.string);
                return _.some(test.names, function (n) {
                    return _.includes(_.toLower(n.name), searchLower);
                });
            };

            $scope.setFilterCategory = function (categoryName) {
                $scope.activeFilterCategory = categoryName;
            };

            $scope.setTypeFilter = function (type) {
                $scope.activeTypeFilter = ($scope.activeTypeFilter === type) ? type : type;
            };

            var isPanel = function (test) {
                return test.conceptClass.name === 'LabSet' || test.conceptClass.name === 'Set';
            };

            var isLabTest = function (test) {
                return test.conceptClass.name === 'Test' || test.conceptClass.name === 'LabTest';
            };

            $scope.matchesTypeFilter = function (test) {
                if (!$scope.activeTypeFilter) return true;
                if ($scope.activeTypeFilter === 'panels') return isPanel(test);
                if ($scope.activeTypeFilter === 'labtest') return isLabTest(test);
                if ($scope.activeTypeFilter === 'other') return !isPanel(test) && !isLabTest(test);
                return true;
            };

            $scope.getTypeCount = function (type) {
                var template = $scope.getOrderTemplate($scope.activeTab.name);
                if (!template || !template.setMembers) return 0;
                var count = 0;
                _.forEach(template.setMembers, function (cat) {
                    _.forEach(cat.setMembers || [], function (test) {
                        if (type === 'panels' && isPanel(test)) count++;
                        else if (type === 'labtest' && isLabTest(test)) count++;
                        else if (type === 'other' && !isPanel(test) && !isLabTest(test)) count++;
                    });
                });
                return count;
            };

            $scope.hasVisibleTestsInGroup = function (className) {
                var template = $scope.getOrderTemplate($scope.activeTab.name);
                if (!template || !template.setMembers || !$scope.activeTab.leftCategory) return false;
                var leftCat = $scope.activeTab.leftCategory;
                return _.some(leftCat.setMembers || [], function (test) {
                    if (test.conceptClass.name !== className) return false;
                    if (!$scope.matchesTypeFilter(test)) return false;
                    if ($scope.search.string && !_.some(test.names, function (n) {
                        return _.includes(_.toLower(n.name), _.toLower($scope.search.string));
                    })) return false;
                    return true;
                });
            };

            $scope.getTotalTestCount = function () {
                var template = $scope.getOrderTemplate($scope.activeTab.name);
                if (!template || !template.setMembers) return 0;
                var count = 0;
                _.forEach(template.setMembers, function (cat) {
                    count += (cat.setMembers || []).length;
                });
                return count;
            };

            $scope.getCategoryTestCount = function (className) {
                var template = $scope.getOrderTemplate($scope.activeTab.name);
                if (!template || !template.setMembers) return 0;
                var count = 0;
                _.forEach(template.setMembers, function (cat) {
                    _.forEach(cat.setMembers || [], function (test) {
                        if (test.conceptClass.name === className) {
                            count++;
                        }
                    });
                });
                return count;
            };

            $scope.getVisibleTestCount = function (className) {
                var template = $scope.getOrderTemplate($scope.activeTab.name);
                if (!template || !template.setMembers || !$scope.activeTab.leftCategory) return 0;
                var leftCat = $scope.activeTab.leftCategory;
                var count = 0;
                _.forEach(leftCat.setMembers || [], function (test) {
                    if (test.conceptClass.name === className) {
                        if (!$scope.matchesTypeFilter(test)) return;
                        if ($scope.search.string && !_.some(test.names, function (n) {
                            return _.includes(_.toLower(n.name), _.toLower($scope.search.string));
                        })) return;
                        count++;
                    }
                });
                return count;
            };

            $scope.getSearchResultCount = function () {
                if (!$scope.search.string) return 0;
                var template = $scope.getOrderTemplate($scope.activeTab.name);
                if (!template || !template.setMembers) return 0;
                var count = 0;
                _.forEach(template.setMembers, function (cat) {
                    _.forEach(cat.setMembers || [], function (test) {
                        if (_.some(test.names, function (n) {
                            return _.includes(_.toLower(n.name), _.toLower($scope.search.string));
                        })) {
                            count++;
                        }
                    });
                });
                return count;
            };

            var checkNameForUnavailableKeywords = function (nameStr) {
                if (!nameStr || typeof nameStr !== 'string') return false;
                var lower = nameStr.toLowerCase();
                return lower.indexOf('[inactive]') !== -1 ||
                       lower.indexOf('[deactive]') !== -1 ||
                       lower.indexOf('[deactivated]') !== -1 ||
                       lower.indexOf('[stock out]') !== -1 ||
                       lower.indexOf('[stockout]') !== -1 ||
                       lower.indexOf('[out of stock]') !== -1 ||
                       lower.indexOf('(inactive)') !== -1 ||
                       lower.indexOf('(deactive)') !== -1 ||
                       lower.indexOf('(stock out)') !== -1 ||
                       lower.indexOf('(out of stock)') !== -1;
            };

            var extractTestName = function (test) {
                if (!test) return '';
                if (typeof test === 'string') return test;
                if (test.name) {
                    if (typeof test.name === 'string') return test.name;
                    if (test.name.display) return test.name.display;
                    if (test.name.name) return test.name.name;
                }
                if (test.displayName) {
                    if (typeof test.displayName === 'string') return test.displayName;
                    if (test.displayName.display) return test.displayName.display;
                    if (test.displayName.name) return test.displayName.name;
                }
                if (test.shortName) {
                    if (typeof test.shortName === 'string') return test.shortName;
                    if (test.shortName.display) return test.shortName.display;
                    if (test.shortName.name) return test.shortName.name;
                }
                if (test.display) return test.display;
                return '';
            };

            var getStockOutMap = function () {
                try {
                    var cached = localStorage.getItem('stockOutTests') || localStorage.getItem('stockStatus');
                    if (cached) {
                        var parsed = JSON.parse(cached);
                        var map = {};
                        if (Array.isArray(parsed)) {
                            parsed.forEach(function (item) {
                                if (typeof item === 'string') map[item.toLowerCase().trim()] = true;
                                else if (item.testName) map[item.testName.toLowerCase().trim()] = true;
                                else if (item.name) map[item.name.toLowerCase().trim()] = true;
                                else if (item.conceptUuid) map[item.conceptUuid] = true;
                            });
                        } else if (typeof parsed === 'object') {
                            Object.keys(parsed).forEach(function (k) {
                                map[k.toLowerCase().trim()] = true;
                            });
                        }
                        return map;
                    }
                } catch (e) {}
                return {};
            };

            $scope.isTestUnavailable = function (test) {
                if (!test) return false;
                if (test.retired === true || test.retired === 'true') return true;
                if (test.active === false || test.active === 'false') return true;
                if (test.isActive === 'N' || test.isActive === 'n' || test.isActive === false) return true;
                if (test.isAvailable === false || test.isAvailable === 'false') return true;
                if (test.status && (test.status.toLowerCase() === 'stockout' || test.status.toLowerCase() === 'inactive' || test.status.toLowerCase() === 'deactive')) return true;

                var testNameStr = extractTestName(test);
                if (checkNameForUnavailableKeywords(testNameStr)) return true;

                var cleanName = testNameStr.toLowerCase().trim();
                if (cleanName && $scope.openelisInactiveTests && $scope.openelisInactiveTests[cleanName]) {
                    return true;
                }

                if (Array.isArray(test.names)) {
                    for (var i = 0; i < test.names.length; i++) {
                        var n = test.names[i];
                        var nStr = typeof n === 'string' ? n : (n.name || n.display || '');
                        var nStrTrim = nStr.trim();
                        if (nStrTrim === '$inactive' || nStrTrim === '$stockout' || checkNameForUnavailableKeywords(nStrTrim)) {
                            return true;
                        }
                        var nLower = nStrTrim.toLowerCase();
                        if (nLower && $scope.openelisInactiveTests && $scope.openelisInactiveTests[nLower]) {
                            return true;
                        }
                    }
                }

                var stockOutMap = getStockOutMap();
                if (cleanName && stockOutMap[cleanName]) return true;
                if (test.uuid && stockOutMap[test.uuid]) return true;
                if (test.uuid && $scope.openelisInactiveTests && $scope.openelisInactiveTests[test.uuid]) return true;

                return false;
            };

            $scope.isTestInactive = $scope.isTestUnavailable;

            $scope.hasUnavailableTests = function () {
                var template = $scope.getOrderTemplate($scope.activeTab.name);
                if (!template || !template.setMembers) return false;
                return _.some(template.setMembers, function (cat) {
                    return _.some(cat.setMembers || [], function (test) {
                        return $scope.isTestUnavailable(test);
                    });
                });
            };

            $scope.hasUnavailableSelectedOrders = function () {
                if ($scope.referralOrders && $scope.referralOrders.length > 0) return true;
                return _.some($scope.selectedOrders, function (order) {
                    var testObj = order.concept || order;
                    return $scope.isTestUnavailable(testObj);
                });
            };

            $scope.printStockOutNotice = function (specificOrder) {
                var testsToPrint = [];
                if (specificOrder) {
                    var sName = extractTestName(specificOrder.concept || specificOrder);
                    testsToPrint.push({
                        name: sName || 'Unknown Test',
                        sampleType: specificOrder.sampleType || specificOrder.sectionName || 'Laboratory'
                    });
                } else if ($scope.referralOrders && $scope.referralOrders.length > 0) {
                    testsToPrint = _.map($scope.referralOrders, function (order) {
                        return {
                            name: order.name || extractTestName(order.concept || order) || 'Unknown Test',
                            sampleType: order.sampleType || 'Laboratory'
                        };
                    });
                } else {
                    var unavail = _.filter($scope.selectedOrders, function (order) {
                        return $scope.isTestUnavailable(order.concept || order);
                    });
                    if (unavail.length === 0) {
                        unavail = $scope.selectedOrders;
                    }
                    testsToPrint = _.map(unavail, function (order) {
                        var name = extractTestName(order.concept || order);
                        return {
                            name: name || 'Unknown Test',
                            sampleType: order.sampleType || order.sectionName || 'Laboratory'
                        };
                    });
                }

                if (testsToPrint.length === 0) {
                    alert("No tests selected for Stock-Out Notice.");
                    return;
                }

                var patient = $scope.patient || ($rootScope && $rootScope.patient) || {};
                var patientName = patient.name || ((patient.givenName || '') + ' ' + (patient.familyName || '')).trim() || 'Patient';
                var patientId = patient.identifier || '';
                var patientAge = patient.age || '';
                var patientGender = patient.gender || '';

                var user = ($rootScope && $rootScope.currentUser) || $scope.currentUser;
                var clinicianName = '';
                if (user) {
                    if (user.provider && user.provider.display) clinicianName = user.provider.display.replace(/\s*-\s*\d+$/, '').trim();
                    else if (user.provider && user.provider.name) clinicianName = user.provider.name;
                    else clinicianName = user.username || '';
                }
                if (!clinicianName && $rootScope && $rootScope.currentProvider && $rootScope.currentProvider.display) {
                    clinicianName = $rootScope.currentProvider.display.replace(/\s*-\s*\d+$/, '').trim();
                }

                var now = new Date();
                var dateStr = now.toLocaleDateString() + ' ' + now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                var noticeNo = 'SO-' + now.getFullYear() + ('0' + (now.getMonth() + 1)).slice(-2) + ('0' + now.getDate()).slice(-2) + '-' + Math.floor(1000 + Math.random() * 9000);

                var printWin = window.open('', '_blank', 'width=800,height=700');
                if (!printWin) {
                    alert("Please allow popups to print the Stock-Out Notice.");
                    return;
                }

                var html = '<!DOCTYPE html><html><head><meta charset="utf-8">';
                html += '<title>Laboratory Reagent Stock-Out Notice - Boru Meda Hospital</title>';
                html += '<style>';
                html += 'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; margin: 30px; font-size: 13px; color: #222; }';
                html += '.header { text-align: center; border-bottom: 2px solid #2c3e50; padding-bottom: 12px; margin-bottom: 16px; }';
                html += '.header h1 { margin: 0; font-size: 18px; color: #1e3a8a; text-transform: uppercase; letter-spacing: 0.5px; }';
                html += '.header h2 { margin: 4px 0 0 0; font-size: 14px; color: #dc2626; font-weight: bold; }';
                html += '.meta-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px 16px; margin: 16px 0; background: #f8fafc; border: 1px solid #e2e8f0; padding: 12px; border-radius: 4px; }';
                html += '.meta-item { display: flex; gap: 8px; font-size: 12px; }';
                html += '.meta-label { font-weight: bold; color: #475569; min-width: 110px; }';
                html += '.meta-val { color: #0f172a; font-weight: 500; }';
                html += 'table { width: 100%; border-collapse: collapse; margin: 16px 0; }';
                html += 'th, td { border: 1px solid #cbd5e1; padding: 8px 10px; font-size: 12px; text-align: left; }';
                html += 'th { background: #f1f5f9; color: #1e293b; font-weight: bold; }';
                html += '.badge-so { background: #fee2e2; color: #b91c1c; font-weight: bold; padding: 2px 6px; border-radius: 3px; font-size: 11px; display: inline-block; }';
                html += '.notice-box { border: 1px solid #f87171; background: #fff1f2; border-radius: 4px; padding: 12px; margin: 16px 0; }';
                html += '.notice-box h4 { margin: 0 0 6px 0; color: #991b1b; font-size: 12px; text-transform: uppercase; }';
                html += '.notice-box ol { margin: 0; padding-left: 20px; font-size: 12px; color: #7f1d1d; }';
                html += '.sig-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; margin-top: 50px; }';
                html += '.sig-box { border-top: 1px solid #000; padding-top: 6px; text-align: center; font-size: 11px; }';
                html += '.footer { text-align: center; font-size: 10px; color: #64748b; margin-top: 30px; border-top: 1px dashed #cbd5e1; padding-top: 8px; }';
                html += '@media print { body { margin: 15mm; } .no-print { display: none; } }';
                html += '</style></head><body>';

                html += '<div class="header">';
                html += '<h1>Boru Meda General Hospital</h1>';
                html += '<div style="font-size:12px;color:#475569;margin-top:2px;">Laboratory & Diagnostic Services Department</div>';
                html += '<h2>LABORATORY REAGENT STOCK-OUT NOTICE</h2>';
                html += '</div>';

                html += '<div class="meta-grid">';
                html += '<div class="meta-item"><span class="meta-label">Notice Ref:</span><span class="meta-val">' + noticeNo + '</span></div>';
                html += '<div class="meta-item"><span class="meta-label">Date & Time:</span><span class="meta-val">' + dateStr + '</span></div>';
                html += '<div class="meta-item"><span class="meta-label">Patient Name:</span><span class="meta-val">' + patientName + '</span></div>';
                html += '<div class="meta-item"><span class="meta-label">Patient ID (MRN):</span><span class="meta-val">' + (patientId || 'N/A') + '</span></div>';
                if (patientAge || patientGender) {
                    html += '<div class="meta-item"><span class="meta-label">Age / Gender:</span><span class="meta-val">' + (patientAge ? patientAge + ' yrs' : '') + (patientGender ? ' / ' + patientGender : '') + '</span></div>';
                }
                if (clinicianName) {
                    html += '<div class="meta-item"><span class="meta-label">Ordering Clinician:</span><span class="meta-val">' + clinicianName + '</span></div>';
                }
                html += '</div>';

                html += '<h3 style="font-size:13px;color:#1e293b;margin:12px 0 6px 0;">Affected Unperformed Test(s)</h3>';
                html += '<table>';
                html += '<thead><tr><th style="width:35px;">#</th><th>Test Name</th><th>Category / Section</th><th>Reason</th><th>Status</th></tr></thead>';
                html += '<tbody>';
                testsToPrint.forEach(function (t, idx) {
                    html += '<tr>';
                    html += '<td>' + (idx + 1) + '</td>';
                    html += '<td><strong>' + t.name + '</strong></td>';
                    html += '<td>' + t.sampleType + '</td>';
                    html += '<td>Reagent Stock Out / Consumables Depleted</td>';
                    html += '<td><span class="badge-so">STOCK-OUT</span></td>';
                    html += '</tr>';
                });
                html += '</tbody></table>';

                html += '<div class="notice-box">';
                html += '<h4>Clinical Instructions & Next Steps</h4>';
                html += '<ol>';
                html += '<li>The requested test(s) listed above could not be processed due to temporary reagent/cartridge stock-out.</li>';
                html += '<li>The patient is advised to consult their attending clinician for alternative diagnostic evaluation or referral.</li>';
                html += '<li>Billing has been marked non-billable / void for the affected tests.</li>';
                html += '</ol>';
                html += '</div>';

                html += '<div class="sig-grid">';
                html += '<div class="sig-box"><p style="margin:0;font-weight:bold;">Ordering Clinician / Laboratory Officer</p><p style="margin:4px 0 0 0;color:#64748b;">Signature & Stamp</p></div>';
                html += '<div class="sig-box"><p style="margin:0;font-weight:bold;">Patient / Guardian</p><p style="margin:4px 0 0 0;color:#64748b;">Signature / Acknowledgement</p></div>';
                html += '</div>';

                html += '<div class="footer">';
                html += 'Boru Meda General Hospital &bull; Electronic Medical Record System &bull; Generated on ' + dateStr;
                html += '</div>';

                html += '<div class="no-print" style="margin-top:20px;text-align:center;">';
                html += '<button onclick="window.print()" style="padding:8px 20px;font-size:14px;background:#1e3a8a;color:#fff;border:none;border-radius:4px;cursor:pointer;font-weight:bold;margin-right:10px;">Print Notice</button>';
                html += '<button onclick="window.close()" style="padding:8px 20px;font-size:14px;background:#64748b;color:#fff;border:none;border-radius:4px;cursor:pointer;">Close</button>';
                html += '</div>';

                html += '</body></html>';

                printWin.document.open();
                printWin.document.write(html);
                printWin.document.close();
                printWin.focus();
                setTimeout(function () {
                    try {
                        printWin.print();
                    } catch (e) {
                        console.error("Print error:", e);
                    }
                }, 500);
            };

            var buildAllCategories = function () {
                var classes = {};
                var template = $scope.getOrderTemplate($scope.activeTab.name);
                if (template && template.setMembers) {
                    _.forEach(template.setMembers, function (cat) {
                        _.forEach(cat.setMembers || [], function (test) {
                            if (test.conceptClass && test.conceptClass.name) {
                                classes[test.conceptClass.name] = test.conceptClass.description || test.conceptClass.name;
                            }
                        });
                    });
                }
                $scope.allCategories = _.sortBy(_.map(Object.keys(classes), function (name) {
                    return {name: name, description: classes[name]};
                }), 'name');
            };

            $scope.toggleOrderSelection = function (test) {
                $scope.resetSearchString();
                if ($scope.isTestUnavailable(test)) {
                    var idx = _.findIndex($scope.referralOrders, function (r) {
                        return r.uuid === test.uuid || (r.concept && r.concept.uuid === test.uuid);
                    });
                    var resolvedName = $scope.getName(test) || extractTestName(test) || "Test";
                    if (idx === -1) {
                        $scope.referralOrders.push({
                            uuid: test.uuid,
                            name: resolvedName,
                            displayName: resolvedName,
                            concept: test,
                            sample: test,
                            isUnavailable: true
                        });
                        createOrder(test);
                        var ord = _.find($scope.consultation.orders, function (o) {
                            return o.concept && o.concept.uuid === test.uuid;
                        });
                        if (ord) {
                            ord.isUnavailable = true;
                            ord.hasBeenModified = true;
                            ord.commentToFulfiller = '[Stock-Out: Reagent Unavailable]';
                            if (ord.concept) {
                                ord.concept.name = ord.concept.name || resolvedName;
                                ord.concept.displayName = ord.concept.displayName || resolvedName;
                            }
                        }
                    } else {
                        $scope.referralOrders.splice(idx, 1);
                        removeOrder(test.uuid);
                    }
                    $scope.updateSelectedOrdersForActiveTab();
                    return;
                }

                var orderPresent = $scope.isActiveOrderPresent(test);
                if (!orderPresent) {
                    createOrder(test);
                    _.each(test.setMembers, function (child) {
                        removeOrder(child.uuid);
                    });
                } else {
                    removeOrder(test.uuid);
                }
            };

            $scope.printOutsideReferralSlip = $scope.printStockOutNotice;

            $scope.toggleAutomaticOrderSelection = function (test) {
                $scope.resetSearchString();
                var orderPresent = $scope.isActiveOrderPresent(test);

                if (!orderPresent) {
                    test.automatic = true;
                    createOrder(test);
                    _.each(test.setMembers, function (child) {
                        removeOrder(child.uuid);
                    });
                } else {
                    var uniqueUUIDs = {}; // Object to store unique UUIDs
                    _.each(test.setMembers, function (child) {
                        uniqueUUIDs[child.uuid] = true; // Store each UUID as a key
                    });

                    // Iterate over unique UUIDs and remove orders
                    for (var uuid in uniqueUUIDs) {
                        if (uniqueUUIDs.hasOwnProperty(uuid)) {
                            removeOrder(uuid);
                        }
                    }
                }
            };

            $scope.isActiveOrderPresent = function (test) {
                var validOrders = _.filter($scope.consultation.orders, function (testOrder) {
                    return !testOrder.isDiscontinued;
                });
                return _.find(validOrders, function (order) {
                    return (order.concept.uuid === test.uuid) || _.includes(testConceptToParentsMapping[test.uuid], order.concept.uuid);
                });
            };

            $scope.isOrderNotEditable = function (order) {
                var test = findTest(order.concept.uuid);
                return $scope.isTestIndirectlyPresent(test);
            };

            $scope.isTestIndirectlyPresent = function (test) {
                var validOrders = _.filter($scope.consultation.orders, function (testOrder) {
                    return !testOrder.isDiscontinued;
                });
                return _.find(validOrders, function (order) {
                    return _.includes(testConceptToParentsMapping[test.uuid], order.concept.uuid);
                });
            };

            $scope.openNotesPopup = function (order) {
                order.previousNote = order.commentToFulfiller;
                $scope.orderNoteText = order.previousNote;
                $scope.dialog = ngDialog.open({ template: 'consultation/views/orderNotes.html', className: 'selectedOrderNoteContainer-dialog ngdialog-theme-default', data: order, scope: $scope
                });
            };

            $scope.openLabNotePopup = function (order) {
                $scope.labNoteData = { text: order.labNote || '' };
                $scope.currentLabNoteOrder = order;
                $scope.dialog = ngDialog.open({
                    templateUrl: 'consultation/views/labNote.html',
                    className: 'ngdialog-theme-default',
                    scope: $scope
                });
            };

            $scope.saveLabNote = function () {
                var order = $scope.currentLabNoteOrder;
                if (order) {
                    order.labNote = $scope.labNoteData.text;
                    if (order.labNote) {
                        var noteTag = '[LAB_NOTE:' + order.labNote + ']';
                        if (!order.commentToFulfiller || order.commentToFulfiller.indexOf('[LAB_NOTE:') === -1) {
                            order.commentToFulfiller = noteTag + (order.commentToFulfiller ? ' ' + order.commentToFulfiller : '');
                        } else {
                            order.commentToFulfiller = order.commentToFulfiller.replace(/\[LAB_NOTE:[^\]]*\]/, noteTag);
                        }
                        if (order.uuid) { order.hasBeenModified = true; }
                    } else {
                        if (order.commentToFulfiller) {
                            order.commentToFulfiller = order.commentToFulfiller.replace(/\[LAB_NOTE:[^\]]*\]\s*/g, '');
                        }
                    }
                }
                $scope.closePopup();
            };

            $scope.clearLabNote = function () {
                $scope.labNoteData.text = '';
            };

            $scope.$on('ngDialog.opened', function () {
                $('body').addClass('show-controller-back');
            });

            $scope.$on('ngDialog.closed', function () {
                $('body').removeClass('show-controller-back');
            });

            $scope.appendPrintNotes = function (order) {
                var printNotes = $translate.instant("Notes: " + '\n' + "Need Print For This Order,");
                if (order.previousNote && order.previousNote.indexOf(printNotes) == -1) {
                    $scope.orderNoteText = printNotes + (order.previousNote || '');
                } else if (($scope.orderNoteText || '').indexOf(printNotes) == -1) {
                    $scope.orderNoteText = ($scope.orderNoteText || '') + $translate.instant(printNotes) + "\n" + "\n";
                }
            };
            $scope.appendClinicalData = function (order) {
                var visitUuid = ($scope.visitHistory && $scope.visitHistory.activeVisit) ? $scope.visitHistory.activeVisit.uuid : null;
                diagnosisService.getDiagnoses($scope.patient.uuid, visitUuid).then(function (response) {
                    var data = response.data;
                    var printDiagnosis = "";
                    if (data && data.length > 0) {
                        var all_diag = data.reduce(function (element, all) {
                            return element + '\n' + "# " + all.codedAnswer.name + ", ";
                        }, " ");
                        printDiagnosis = $translate.instant("Diagnoses:" + all_diag);
                    } else {
                        printDiagnosis = $translate.instant("No diagnosis yet,");
                    }
                    if (order.previousNote && order.previousNote.indexOf(printDiagnosis) == -1) {
                        $scope.orderNoteText = (order.previousNote || '') + printDiagnosis;
                    } else if (($scope.orderNoteText || '').indexOf(printDiagnosis) == -1) {
                        $scope.orderNoteText = ($scope.orderNoteText || '') + $translate.instant(printDiagnosis) + '\n' + '\n';
                    }
                });
            };
            $scope.isPrintShown = function (isOrderSaved) {
                var configuredOptions = getConfiguredOptions();
                return _.some(configuredOptions, function (option) {
                    return option.toLowerCase() === 'needsprint';
                })
                    && !isOrderSaved;
            };
            $scope.isUrgent = function () {
                var configuredOptions = getConfiguredOptions();
                return _.some(configuredOptions, function (option) {
                    return option.toLowerCase() === 'urgent';
                });
            };
            var getConfiguredOptions = function () {
                var configuredOptions = null;
                if ($scope.activeTab.name == 'Radiology') {
                    configuredOptions = $scope.enableRadiologyOrderOptions;
                } else {
                    configuredOptions = $scope.enableLabOrderOptions;
                }
                return configuredOptions;
            };
            $scope.setEditedFlag = function (order, orderNoteText) {
                if (order.previousNote !== orderNoteText) {
                    order.commentToFulfiller = orderNoteText;
                    order.hasBeenModified = true;
                }
                $scope.closePopup();
            };

            $scope.closePopup = function () {
                ngDialog.close();
            };

            // Define an array to store the samples that have been sent
            var sentSamples = [];

            $scope.getName = function (sample) {
                if (!sample) return '';
                var name = _.find(sample.names, { conceptNameType: "SHORT" }) || _.find(sample.names, { conceptNameType: "FULLY_SPECIFIED" });
                var nameStr = (name && name.name) ? name.name : (sample.name ? (sample.name.display || sample.name.name || sample.name) : (sample.displayName || ''));

                // Check if the sample has already been sent
                if (sentSamples.includes(sample)) {
                    return nameStr;
                }
                var createOrderCalled = false;
                var remove = false;

                if (Array.isArray(sample.names)) {
                    sample.names.forEach(function (test) {
                        if (test.conceptNameType === "FULLY_SPECIFIED" && orderableTests.includes(test.name)) {
                            $scope.toggleAutomaticOrderSelection(sample);
                            createOrderCalled = true;
                        }
                    });
                }

                if (!createOrderCalled && $scope.consultation && $scope.consultation.orders) {
                    $scope.consultation.orders.forEach(function (order) {
                        if (order.automatic === true && order.concept && order.concept.uuid === sample.uuid) {
                            remove = true;
                        }
                    });

                    if (remove) {
                        removeOrder(sample.uuid);
                    }
                }

                if (createOrderCalled) {
                    sentSamples.push(sample);
                }

                return nameStr;
            };

            $scope.getTestColor = function (test) {
                if ($scope.isTestUnavailable(test)) {
                    return { "color": "#c0392b", "font-weight": "bold" };
                }
                return {};
            };

            $scope.getNameInDefaultLocale = function (sample) {
                var name = _.find(sample.names, { conceptNameType: "FULLY_SPECIFIED", locale: localStorage.getItem("openmrsDefaultLocale") || "en" });
                return name ? name.name : (sample.name ? (sample.name.name || sample.name.display || sample.name) : (sample.displayName || ''));
            };

            init();
        }]);
