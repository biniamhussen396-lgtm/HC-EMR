'use strict';

angular.module('bahmni.orders')
    .controller('OrderSearchController', ['$scope', '$rootScope', '$state', '$http', '$q', 'spinner', 'messagingService', '$translate',
        function ($scope, $rootScope, $state, $http, $q, spinner, messagingService, $translate) {

            $scope.activeTab = 'new'; // 'new' or 'backlog'
            $scope.selectedOrderType = 'All';
            $scope.loading = false;

            $scope.orderTypes = [
                { label: 'All Orders', value: 'All', icon: 'fa-th-large' },
                { label: 'Radiology', value: 'Radiology Order', icon: 'fa-film' },
                { label: 'Procedure', value: 'Procedure Order', icon: 'fa-medkit' },
                { label: 'Ophthalmology', value: 'Ophtha Order', icon: 'fa-eye' },
                { label: 'Pathology', value: 'Pathology Order', icon: 'fa-flask' }
            ];

            $scope.filters = {
                name: '',
                identifier: '',
                date: '',
                datePreset: 'all'
            };

            $scope.newOrders = [];
            $scope.backlogOrders = [];

            var fetchOrders = function () {
                $scope.loading = true;
                var promiseNew = $http.get('/openmrs/ws/rest/v1/bahmnicore/sql', {
                    params: { q: 'emrapi.sqlSearch.newOrdersSearch' },
                    withCredentials: true
                });

                var promiseBacklog = $http.get('/openmrs/ws/rest/v1/bahmnicore/sql', {
                    params: { q: 'emrapi.sqlSearch.backlogOrdersSearch' },
                    withCredentials: true
                });

                return $q.all([promiseNew, promiseBacklog]).then(function (results) {
                    $scope.newOrders = results[0].data || [];
                    $scope.backlogOrders = results[1].data || [];
                    $scope.loading = false;
                }).catch(function (error) {
                    console.error('Error fetching orders:', error);
                    $scope.loading = false;
                    messagingService.showMessage('error', 'Error loading orders list');
                });
            };

            $scope.switchTab = function (tab) {
                $scope.activeTab = tab;
            };

            $scope.setOrderType = function (orderType) {
                $scope.selectedOrderType = orderType;
            };

            $scope.setDatePreset = function (preset) {
                $scope.filters.datePreset = preset;
                var today = new Date();
                if (preset === 'all') {
                    $scope.filters.date = '';
                } else if (preset === 'yesterday') {
                    var yest = new Date(today);
                    yest.setDate(yest.getDate() - 1);
                    $scope.filters.date = yest.toISOString().split('T')[0];
                } else if (preset === 'today') {
                    $scope.filters.date = today.toISOString().split('T')[0];
                }
            };

            $scope.clearFilters = function () {
                $scope.filters.name = '';
                $scope.filters.identifier = '';
                $scope.filters.date = '';
                $scope.filters.datePreset = 'all';
                $scope.selectedOrderType = 'All';
            };

            $scope.hasActiveFilters = function () {
                return $scope.filters.name || $scope.filters.identifier || $scope.filters.date || $scope.selectedOrderType !== 'All';
            };

            $scope.getFilteredOrders = function () {
                var list = $scope.activeTab === 'new' ? $scope.newOrders : $scope.backlogOrders;

                return list.filter(function (order) {
                    // Order Type Filter
                    if ($scope.selectedOrderType !== 'All' && order.orderType !== $scope.selectedOrderType) {
                        return false;
                    }

                    // Name Filter (case-insensitive substring match)
                    if ($scope.filters.name && $scope.filters.name.trim() !== '') {
                        var searchName = $scope.filters.name.toLowerCase().trim();
                        var patientName = (order.name || '').toLowerCase();
                        if (patientName.indexOf(searchName) === -1) {
                            return false;
                        }
                    }

                    // Identifier / MRN Filter (case-insensitive substring match)
                    if ($scope.filters.identifier && $scope.filters.identifier.trim() !== '') {
                        var searchId = $scope.filters.identifier.toLowerCase().trim();
                        var patientId = (order.identifier || '').toLowerCase();
                        if (patientId.indexOf(searchId) === -1) {
                            return false;
                        }
                    }

                    // Date Filter (only for Backlog)
                    if ($scope.activeTab === 'backlog' && $scope.filters.date && $scope.filters.date.trim() !== '') {
                        var selectedDate = $scope.filters.date.trim();
                        if (order.orderDateOnly !== selectedDate) {
                            return false;
                        }
                    }

                    return true;
                });
            };

            $scope.goToFulfillment = function (order) {
                if (!order || !order.uuid || !order.orderType) return;
                $state.go('orderFulfillment', {
                    patientUuid: order.uuid,
                    orderType: order.orderType
                });
            };

            $scope.getOrderTypeBadgeClass = function (orderType) {
                switch (orderType) {
                    case 'Radiology Order': return 'badge-radiology';
                    case 'Procedure Order': return 'badge-procedure';
                    case 'Ophtha Order': return 'badge-ophtha';
                    case 'Pathology Order': return 'badge-pathology';
                    default: return 'badge-default';
                }
            };

            $scope.refresh = function () {
                spinner.forPromise(fetchOrders());
            };

            // Initialize
            $scope.refresh();
        }
    ]);
