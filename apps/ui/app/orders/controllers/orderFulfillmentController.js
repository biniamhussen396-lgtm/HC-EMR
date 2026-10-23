"use strict";

angular.module('bahmni.orders').controller('OrderFulfillmentController', ['userService', '$http', '$scope', '$rootScope', '$stateParams', '$state', '$q', 'patientContext', 'orderService', 'observationsService', 'orderObservationService',
    'orderTypeService', 'sessionService', 'encounterService', 'spinner', 'messagingService', 'appService', '$anchorScroll', 'orderFulfillmentConfig', 'contextChangeHandler', '$translate', 'paymentStatusService',
    function (userService, $http, $scope, $rootScope, $stateParams, $state, $q, patientContext, orderService, observationsService, orderObservationService,
        orderTypeService, sessionService, encounterService, spinner, messagingService, appService, $anchorScroll, orderFulfillmentConfig, contextChangeHandler, $translate, paymentStatusService) {
        $scope.patient = patientContext.patient;
        var currentUser = $rootScope.currentUser || $scope.currentUser || { privileges: [] };
        $scope.patient.docpriv = (currentUser.privileges || []).filter(function (priv) {
            return priv.name == 'Write Radiology note';
        });
        $scope.$on("event:confirmSuggestion", function (event, uniqueId) {


            $scope.orders.forEach(function (order) {
                if (order.bahmniObservations[0] && order.bahmniObservations[0].groupMembers[0].groupMembers[2].uniqueId == uniqueId) order.bahmniObservations[0].groupMembers[0].groupMembers[0].value = (order.bahmniObservations[0].groupMembers[0].groupMembers[1].readOnly || "")
            })
        })
        var payment_config = appService.getAppDescriptor().getConfigValue("paymentConfig");
        var ordersSerialNumberBuilding = appService.getAppDescriptor().getConfigValue("ordersSerialNumberBuilding");
        $scope.formName = $stateParams.orderType + Bahmni.Common.Constants.fulfillmentFormSuffix;
        $scope.fulfillmentConfig = orderFulfillmentConfig;
        $scope.orderType = $stateParams.orderType;
        $scope.nextPageLoading = false;
        $scope.orders = [];
        var formData = function (type, patientUui, numberOfVisits, formGroup, patientProgramUuid) {
            var params = {
                s: type,
                patient: patientUui,
                numberOfVisits: numberOfVisits,
                v: "full",
                conceptNames: formGroup || null,
                patientProgramUuid: patientProgramUuid || null
            };
            return $http.get(Bahmni.Common.Constants.formDataUrl, { params: params });
        };
        var testDoc = ["Radiology Notes Suggestion"];

        formData("byPatientUuid", $scope.patient.uuid, 1, testDoc).then(res => {
            $scope.patient.suggested = res.data.results
        })


        var getActiveEncounter = function () {
            var currentProviderUuid = $rootScope.currentProvider ? $rootScope.currentProvider.uuid : null;
            return encounterService.find({
                patientUuid: $scope.patient.uuid,
                providerUuids: !_.isEmpty(currentProviderUuid) ? [currentProviderUuid] : null,
                includeAll: Bahmni.Common.Constants.includeAllObservations,
                locationUuid: sessionService.getLoginLocationUuid()
            }).then(function (encounterTransactionResponse) {
                $scope.encounter = encounterTransactionResponse.data;
                return $scope.encounter;
            });
        };

        var getOrdersSerialNumber = function (uuid) {
            var params = {
                q: "emrapi.getOrdersSerialNumber",
                uuid: uuid,
            };

            return $http({
                method: "GET",
                url: '/openmrs/ws/rest/v1/bahmnicore/sql',
                params: params,
                withCredentials: true
            }).then(function (response) {
                return response.data;
            }).catch(function (error) {
                console.error('Error fetching patient admission data:', error);
                throw error;
            });
        };

        $scope.getOrders = function () {
            var patientUuid = patientContext.patient.uuid;
            $scope.orderTypeUuid = orderTypeService.getOrderTypeUuid($stateParams.orderType);
            var includeObs = true;
            var params = {
                patientUuid: patientUuid,
                orderTypeUuid: $scope.orderTypeUuid,
                conceptNames: $scope.config.conceptNames,
                includeObs: includeObs,
                numberOfVisits: $scope.config.numberOfVisits,
                obsIgnoreList: $scope.config.obsIgnoreList,
                visitUuid: $scope.visitUuid,
                orderUuid: $scope.orderUuid,
                locationUuids: $rootScope.facilityLocationUuids
            };
            return orderService.getOrders(params).then(function (response) {
                var data = response.data;
                $scope.orders.push.apply($scope.orders, data);
                $scope.orders.forEach(async function (order) {
                    await getOrdersSerialNumber(order.concept.uuid).then(function (data) {
                        ordersSerialNumberBuilding.forEach(config => {
                            if (data[0].concept_set === config.concept_id) {
                                order.serialNumber = config.prefix + "-" + data[0].serialNumber;
                            }
                        });
                    });
                    order.bahmniObservations = _.filter($scope.encounter.observations, function (observation) {
                        return observation.orderUuid === order.orderUuid;
                    }); 

                    if (order.bahmniObservations.length > 0) {
                        order.showForm = true;
                    }
                    getOrderPaymentStatus(order);
                });
            });
        };

        var getOrderPaymentStatus = function (order) {
            paymentStatusService.getPaymentStatus(order.orderUuid).then(function (response) {
                if (!payment_config["disable checking"]) {
                    order.paymentStatus = (response.data && response.data.status === "PAID") || response.data === true;
                }
                else {
                    order.paymentStatus = true;
                }
            }).catch(function () {
                paymentStatusService.getPaymentStatus(patientContext.patient.identifier).then(function (res) {
                    order.paymentStatus = (res.data && res.data.status === "PAID") || res.data === true;
                }).catch(function () {
                    order.paymentStatus = true;
                });
            });
        };

        var getObservationsForOrders = function () {
            var orderLabelConcept = appService.getAppDescriptor().getConfigValue("orderLabelConcept");
            if (orderLabelConcept) {
                return observationsService.fetch(patientContext.patient.uuid, [orderLabelConcept], null, $scope.config.numberOfVisits, $scope.visitUuid, null, false)
                .then(function (response) {
                    $scope.selectedOrderLabel = new Map();
                    var orderObservationsData = _(response.data)
                                .groupBy('orderUuid')
                                .map(function (items, orderUuid, concept) {
                                    return {
                                        orderUuid: orderUuid,
                                        conceptValue: concept[orderUuid][0].value,
                                        dataType: concept[orderUuid][0].concept.dataType
                                    };
                                }).value();
                    orderObservationsData.forEach(function (item) {
                        var orderUuid = item.orderUuid;
                        var dataType = item.dataType;
                        var conceptValue = item.conceptValue;

                        if (dataType === "Coded") {
                            $scope.selectedOrderLabel[orderUuid] = conceptValue.name;
                        } else if (dataType === "Text") {
                            $scope.selectedOrderLabel[orderUuid] = conceptValue;
                        }
                    });
                });
            }
        };
        
        $scope.toggleShowOrderForm = function (order) {
            order.showForm = !order.showForm;
        };

        var init = function () {
            return getActiveEncounter().then($scope.getOrders);
        };

        spinner.forPromise(init());
        $scope.config = $scope.fulfillmentConfig || {};
        $anchorScroll();

        $scope.isFormValid = function () {
            var contxChange = contextChangeHandler.execute();
            var shouldAllow = contxChange["allow"];
            if (!shouldAllow) {
                var errorMessage = contxChange["errorMessage"] ? contxChange["errorMessage"] : "{{'ORDERS_FORM_ERRORS_MESSAGE_KEY' | translate }}";
                messagingService.showMessage('error', errorMessage);
            }
            return shouldAllow;
        };

        $scope.getEmptyMessage = function () {
            return $translate.instant('NO_ORDERS_PRESENT', {orderType: $scope.orderType});
        };

        $scope.$on("event:saveOrderObservations", function () {
            if (!$scope.isFormValid()) {
                $scope.$parent.$broadcast("event:errorsOnForm");
                return $q.when({});
            }
            var savePromise = orderObservationService.save($scope.orders, $scope.patient, sessionService.getLoginLocationUuid());
            spinner.forPromise(savePromise.then(function () {
                $state.transitionTo($state.current, $state.params, {
                    reload: true,
                    inherit: false,
                    notify: true
                }).then(function () {
                    messagingService.showMessage('info', 'Saved');
                });
            }).catch(function (error) {
                var message = $translate.instant("DEFAULT_SERVER_ERROR_MESSAGE");
                try {
                    /* This is a dirty fix to do, the real reason of failure is because of there is no visit type assosiated with
                     save request to create a new visit in mrs.
                      */
                    if (error.data.error.message.indexOf("Visit Type is required") >= 0) {
                        message = $translate.instant("VISIT_CLOSED_CREATE_NEW_ERROR_MESSAGE");
                    }
                } catch (e) { /* ignore the error */ }
                messagingService.showMessage('error', message);
            }));
        });
    }]);