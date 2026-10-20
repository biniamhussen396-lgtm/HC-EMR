'use strict';

angular.module('admin')
    .controller('BackupRestoreController', ['$scope', '$http', '$interval', '$timeout', 'messagingService',
        function ($scope, $http, $interval, $timeout, messagingService) {
            $scope.backups = [];
            $scope.status = {
                status: 'idle',
                progress: 0,
                message: 'Loading...',
                logs: []
            };
            $scope.loading = true;
            $scope.selectedForRestore = null;
            $scope.confirmModalVisible = false;
            var pollPromise = null;

            var API_BASE = '/backup-api';

            $scope.fetchBackups = function () {
                $scope.loading = true;
                $http.get(API_BASE + '/backups').then(function (response) {
                    $scope.loading = false;
                    if (response.data && response.data.backups) {
                        $scope.backups = response.data.backups;
                    }
                    if (response.data && response.data.status) {
                        $scope.status = response.data.status;
                        if ($scope.status.status === 'running') {
                            startPolling();
                        }
                    }
                }, function (error) {
                    $scope.loading = false;
                    $scope.status.message = 'Unable to connect to Backup Service. Verify the service is running.';
                });
            };

            var pollStatus = function () {
                $http.get(API_BASE + '/status').then(function (response) {
                    $scope.status = response.data;
                    if ($scope.status.status !== 'running') {
                        stopPolling();
                        $scope.fetchBackups();
                        if ($scope.status.status === 'completed') {
                            messagingService.showMessage('info', 'Operation completed successfully!');
                        } else if ($scope.status.status === 'error') {
                            messagingService.showMessage('error', $scope.status.message || 'Operation encountered an error.');
                        }
                    }
                    // Auto-scroll logs
                    $timeout(function () {
                        var logBox = document.getElementById('backup-log-console');
                        if (logBox) {
                            logBox.scrollTop = logBox.scrollHeight;
                        }
                    }, 50);
                });
            };

            var startPolling = function () {
                if (!pollPromise) {
                    pollPromise = $interval(pollStatus, 2000);
                }
            };

            var stopPolling = function () {
                if (pollPromise) {
                    $interval.cancel(pollPromise);
                    pollPromise = null;
                }
            };

            $scope.startFullBackup = function () {
                if ($scope.status.status === 'running') return;
                $scope.status.status = 'running';
                $scope.status.progress = 5;
                $scope.status.message = 'Starting Full System Backup...';
                $scope.status.logs = ['[INFO] Starting Full System Backup (Databases, Volumes, Modules)...'];
                startPolling();

                $http.post(API_BASE + '/backup/full', {}).then(function (response) {
                    messagingService.showMessage('info', 'Full backup initiated.');
                }, function (err) {
                    stopPolling();
                    $scope.status.status = 'error';
                    $scope.status.message = (err.data && err.data.message) || 'Failed to start full backup';
                });
            };

            $scope.startDbBackup = function () {
                if ($scope.status.status === 'running') return;
                $scope.status.status = 'running';
                $scope.status.progress = 5;
                $scope.status.message = 'Starting Database Backup...';
                $scope.status.logs = ['[INFO] Starting Database Backup (OpenMRS, OpenELIS, Odoo, Reports, PACS)...'];
                startPolling();

                $http.post(API_BASE + '/backup/db', {}).then(function (response) {
                    messagingService.showMessage('info', 'Database backup initiated.');
                }, function (err) {
                    stopPolling();
                    $scope.status.status = 'error';
                    $scope.status.message = (err.data && err.data.message) || 'Failed to start database backup';
                });
            };

            $scope.confirmRestore = function (backup) {
                if ($scope.status.status === 'running') return;
                $scope.selectedForRestore = backup;
                $scope.confirmModalVisible = true;
            };

            $scope.cancelRestore = function () {
                $scope.selectedForRestore = null;
                $scope.confirmModalVisible = false;
            };

            $scope.executeRestore = function () {
                if (!$scope.selectedForRestore) return;
                var backup = $scope.selectedForRestore;
                $scope.confirmModalVisible = false;
                $scope.status.status = 'running';
                $scope.status.progress = 5;
                $scope.status.message = 'Restoring from ' + backup.name + '...';
                $scope.status.logs = ['[INFO] Initiating restore from ' + backup.name];
                startPolling();

                $http.post(API_BASE + '/restore', {archive: backup.name}).then(function (response) {
                    messagingService.showMessage('info', 'Restore process initiated.');
                }, function (err) {
                    stopPolling();
                    $scope.status.status = 'error';
                    $scope.status.message = (err.data && err.data.error) || (err.data && err.data.message) || 'Failed to start restore';
                });
            };

            $scope.$on('$destroy', function () {
                stopPolling();
            });

            // Initial load
            $scope.fetchBackups();
        }
    ]);
