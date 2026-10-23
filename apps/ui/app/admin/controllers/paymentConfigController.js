'use strict';

angular.module('admin')
    .controller('PaymentConfigController', ['$scope', '$rootScope', '$http', '$timeout', 'messagingService',
        function ($scope, $rootScope, $http, $timeout, messagingService) {
            var API_BASE = '/backup-api';

            $scope.loading = true;
            $scope.saving = false;
            $scope.checkingOdoo = false;
            $scope.savedSuccess = false;

            $scope.odooStatus = {
                online: false,
                status_code: 0,
                message: 'Checking Odoo connectivity...',
                checked_url: '',
                checked_at: ''
            };

            $scope.config = {
                registration: {
                    disable_billing: false,
                    payment_window: 30
                },
                orders: {
                    disable_checking: false
                },
                clinical: {
                    disable_checking: false
                }
            };

            $scope.fetchConfig = function () {
                $scope.loading = true;
                $http.get(API_BASE + '/payment-config').then(function (res) {
                    $scope.loading = false;
                    if (res.data) {
                        if (res.data.odoo) {
                            $scope.odooStatus = res.data.odoo;
                        }
                        if (res.data.registration) {
                            $scope.config.registration = res.data.registration;
                        }
                        if (res.data.orders) {
                            $scope.config.orders = res.data.orders;
                        }
                        if (res.data.clinical) {
                            $scope.config.clinical = res.data.clinical;
                        }
                    }
                }, function (err) {
                    $scope.loading = false;
                    messagingService.showMessage('error', 'Unable to retrieve payment configuration from server.');
                });
            };

            $scope.refreshOdooStatus = function () {
                $scope.checkingOdoo = true;
                $http.get(API_BASE + '/payment-config').then(function (res) {
                    $scope.checkingOdoo = false;
                    if (res.data && res.data.odoo) {
                        $scope.odooStatus = res.data.odoo;
                        if (res.data.odoo.online) {
                            messagingService.showMessage('info', 'Odoo service is ONLINE and responding.');
                        } else {
                            messagingService.showMessage('error', 'Odoo service is OFFLINE or unreachable. You can enable Emergency Bypass (Pass Payment) to prevent hospital disruption.');
                        }
                    }
                }, function () {
                    $scope.checkingOdoo = false;
                    messagingService.showMessage('error', 'Error pinging Odoo service.');
                });
            };

            // Preset: Normal mode (Check payment in Odoo)
            $scope.setModeNormal = function () {
                $scope.config.registration.disable_billing = false;
                $scope.config.orders.disable_checking = false;
                $scope.config.clinical.disable_checking = false;
                messagingService.showMessage('info', 'Selected Normal Mode: Odoo payment checks are enforced across Registration, Orders, and Clinical.');
            };

            // Preset: Emergency Bypass (Pass payment without stopping)
            $scope.setModeEmergencyBypass = function () {
                $scope.config.registration.disable_billing = true;
                $scope.config.orders.disable_checking = true;
                $scope.config.clinical.disable_checking = true;
                messagingService.showMessage('info', 'Selected Emergency Mode: All payment checks bypassed (Pass Payment active). Clinical and order workflows will not be stopped by Odoo.');
            };

            $scope.isAllBypassed = function () {
                return $scope.config &&
                       $scope.config.registration &&
                       $scope.config.orders &&
                       $scope.config.clinical &&
                       $scope.config.registration.disable_billing &&
                       $scope.config.orders.disable_checking &&
                       $scope.config.clinical.disable_checking;
            };

            $scope.isAllEnforced = function () {
                return $scope.config &&
                       $scope.config.registration &&
                       $scope.config.orders &&
                       $scope.config.clinical &&
                       !$scope.config.registration.disable_billing &&
                       !$scope.config.orders.disable_checking &&
                       !$scope.config.clinical.disable_checking;
            };

            $scope.saveConfig = function () {
                $scope.saving = true;
                $scope.savedSuccess = false;

                var payload = {
                    registration: {
                        disable_billing: $scope.config.registration.disable_billing,
                        payment_window: parseInt($scope.config.registration.payment_window || 30, 10)
                    },
                    orders: {
                        disable_checking: $scope.config.orders.disable_checking
                    },
                    clinical: {
                        disable_checking: $scope.config.clinical.disable_checking
                    }
                };

                $http.post(API_BASE + '/payment-config', payload).then(function (res) {
                    $scope.saving = false;
                    $scope.savedSuccess = true;
                    if (res.data && res.data.config) {
                        $scope.config = res.data.config;
                        if (res.data.config.odoo) {
                            $scope.odooStatus = res.data.config.odoo;
                        }
                    }
                    var modeName = $scope.isAllBypassed() ? 'Emergency Mode (Pass Payment Active)' : ($scope.isAllEnforced() ? 'Normal Mode (Odoo Enforced)' : 'Custom Payment Rules');
                    messagingService.showMessage('info', 'Payment configuration saved successfully! Effective: ' + modeName);

                    $timeout(function () {
                        $scope.savedSuccess = false;
                    }, 5000);
                }, function (err) {
                    $scope.saving = false;
                    var msg = (err.data && err.data.error) || 'Failed to save payment configuration.';
                    messagingService.showMessage('error', msg);
                });
            };

            $scope.fetchConfig();
        }
    ]);
