'use strict';

angular.module('admin')
    .controller('BackupRestoreController', ['$scope', '$rootScope', '$http', '$interval', '$timeout', 'messagingService',
        function ($scope, $rootScope, $http, $interval, $timeout, messagingService) {
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
            $scope.hasRestorePrivilege = false;
            var pollPromise = null;

            var evaluateRestorePrivilege = function () {
                var user = $rootScope.currentUser;
                if (!user) {
                    $scope.hasRestorePrivilege = false;
                    return;
                }
                var userPrivileges = _.map(user.privileges || [], function (p) {
                    return (p && p.name) ? p.name : p;
                });
                var userRoles = _.map(user.roles || [], function (r) {
                    return (r && r.name) ? r.name : r;
                });

                if (userPrivileges.indexOf('app:admin:restore') !== -1 ||
                    userPrivileges.indexOf('app:admin:backupRestore:restore') !== -1 ||
                    userRoles.indexOf('SuperAdmin') !== -1 ||
                    userRoles.indexOf('System Developer') !== -1 ||
                    userRoles.indexOf('Privilege Level: Full') !== -1 ||
                    (user.username && (user.username === 'admin' || user.username === 'superman'))) {
                    $scope.hasRestorePrivilege = true;
                } else {
                    $scope.hasRestorePrivilege = false;
                }
            };

            evaluateRestorePrivilege();
            $rootScope.$watch('currentUser', function (user) {
                if (user) {
                    evaluateRestorePrivilege();
                }
            });

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
                    var msg = (err.data && typeof err.data === 'object' && (err.data.message || err.data.error)) || 'Failed to start full backup. Backup Service is unreachable.';
                    $scope.status.message = msg;
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
                    var msg = (err.data && typeof err.data === 'object' && (err.data.message || err.data.error)) || 'Failed to start database backup. Backup Service is unreachable.';
                    $scope.status.message = msg;
                });
            };

            // File Upload State
            $scope.selectedUploadFile = null;
            $scope.isUploading = false;
            $scope.uploadProgress = 0;
            $scope.restoreFromUpload = false;

            $scope.onFileSelected = function (element) {
                if (!element || !element.files || element.files.length === 0) return;
                var file = element.files[0];
                var name = file.name || '';
                if (!name.endsWith('.tar.gz') && !name.endsWith('.tgz')) {
                    messagingService.showMessage('error', 'Please select a valid Bahmni backup archive (*.tar.gz).');
                    element.value = '';
                    return;
                }
                $scope.$applyAsync(function () {
                    $scope.selectedUploadFile = {
                        name: file.name,
                        size_mb: (file.size / (1024 * 1024)).toFixed(2),
                        file: file
                    };
                });
            };

            $scope.clearUpload = function () {
                $scope.selectedUploadFile = null;
                $scope.isUploading = false;
                $scope.uploadProgress = 0;
                $scope.restoreFromUpload = false;
                var input = document.getElementById('backupUploadInput');
                if (input) input.value = '';
            };

            $scope.confirmUploadAndRestore = function () {
                if (!$scope.hasRestorePrivilege) {
                    messagingService.showMessage('error', 'Access denied: You do not have permission to restore system backups (app:admin:restore required).');
                    return;
                }
                if (!$scope.selectedUploadFile || $scope.status.status === 'running') return;
                $scope.restoreFromUpload = true;
                $scope.selectedForRestore = {
                    name: $scope.selectedUploadFile.name,
                    size_mb: $scope.selectedUploadFile.size_mb,
                    isUpload: true
                };
                $scope.confirmModalVisible = true;
            };

            $scope.startUpload = function (andRestore) {
                if (!$scope.selectedUploadFile || $scope.isUploading) return;
                if (andRestore && !$scope.hasRestorePrivilege) {
                    messagingService.showMessage('error', 'Access denied: You do not have permission to restore system backups (app:admin:restore required).');
                    return;
                }
                var fileObj = $scope.selectedUploadFile.file;
                $scope.isUploading = true;
                $scope.uploadProgress = 0;

                var url = API_BASE + '/upload?filename=' + encodeURIComponent(fileObj.name) + (andRestore ? '&restore=true' : '');

                var xhr = new XMLHttpRequest();
                xhr.open('POST', url, true);
                xhr.setRequestHeader('Content-Type', 'application/octet-stream');
                xhr.setRequestHeader('X-File-Name', encodeURIComponent(fileObj.name));
                if (andRestore) {
                    xhr.setRequestHeader('X-Restore-Now', 'true');
                }

                xhr.upload.onprogress = function (e) {
                    if (e.lengthComputable) {
                        $scope.$applyAsync(function () {
                            $scope.uploadProgress = Math.round((e.loaded * 100) / e.total);
                        });
                    }
                };

                xhr.onload = function () {
                    $scope.$applyAsync(function () {
                        $scope.isUploading = false;
                        if (xhr.status >= 200 && xhr.status < 300) {
                            var resp = {};
                            try { resp = JSON.parse(xhr.responseText); } catch (e) {}
                            $scope.clearUpload();
                            $scope.fetchBackups();
                            if (andRestore) {
                                messagingService.showMessage('info', 'File uploaded! System restore in progress.');
                                $scope.status.status = 'running';
                                $scope.status.message = 'Restoring from uploaded archive ' + fileObj.name + '...';
                                $scope.status.progress = 10;
                                startPolling();
                            } else {
                                messagingService.showMessage('info', resp.message || 'Backup archive uploaded successfully.');
                            }
                        } else {
                            var errResp = {};
                            try { errResp = JSON.parse(xhr.responseText); } catch (e) {}
                            var errMessage = errResp.error || errResp.message || ('Upload failed with HTTP status ' + xhr.status);
                            messagingService.showMessage('error', errMessage);
                        }
                    });
                };

                xhr.onerror = function () {
                    $scope.$applyAsync(function () {
                        $scope.isUploading = false;
                        messagingService.showMessage('error', 'Network error encountered during backup file upload.');
                    });
                };

                xhr.send(fileObj);
            };

            $scope.confirmRestore = function (backup) {
                if (!$scope.hasRestorePrivilege) {
                    messagingService.showMessage('error', 'Access denied: You do not have permission to restore system backups (app:admin:restore required).');
                    return;
                }
                if ($scope.status.status === 'running') return;
                $scope.selectedForRestore = backup;
                $scope.confirmModalVisible = true;
            };

            $scope.cancelRestore = function () {
                $scope.selectedForRestore = null;
                $scope.confirmModalVisible = false;
                $scope.restoreFromUpload = false;
            };

            $scope.executeRestore = function () {
                if (!$scope.selectedForRestore) return;
                if (!$scope.hasRestorePrivilege) {
                    messagingService.showMessage('error', 'Access denied: You do not have permission to restore system backups (app:admin:restore required).');
                    return;
                }
                var backup = $scope.selectedForRestore;
                $scope.confirmModalVisible = false;

                if (backup.isUpload && $scope.selectedUploadFile) {
                    $scope.startUpload(true);
                    return;
                }

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

            $scope.getDownloadUrl = function (backup) {
                if (!backup || !backup.name) return '';
                return API_BASE + '/download/' + encodeURIComponent(backup.name);
            };

            $scope.$on('$destroy', function () {
                stopPolling();
            });

            // Initial load
            $scope.fetchBackups();
        }
    ]);
