(window["webpackJsonp"] = window["webpackJsonp"] || []).push([[1],{

/***/ 1584:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _constants__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(12);
/* harmony import */ var lodash__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(22);
/* harmony import */ var lodash__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(lodash__WEBPACK_IMPORTED_MODULE_1__);


/*
/*
    Below, we are creating local variables for all the webpack import variables.
    This is avoid seeing `lodash__WEBPACK_IMPORTED_MODULE_1__["map"]` in different places in code.
    This will help to maintain readability since this file might need to be changed on the implementation after deployment.
    For more information check the docs:
    https://bahmni.atlassian.net/wiki/spaces/BAH/pages/927432705/Appointment+Request#Deciding-the-status-of-Appointment-and-Provider-Response%3A
 */

var appointmentStatusList = _constants__WEBPACK_IMPORTED_MODULE_0__[/* APPOINTMENT_STATUSES */ "b"];
var providerResponseList = _constants__WEBPACK_IMPORTED_MODULE_0__[/* PROVIDER_RESPONSES */ "j"];
var map_fn = lodash__WEBPACK_IMPORTED_MODULE_1__["map"];
var isEmpty_fn = lodash__WEBPACK_IMPORTED_MODULE_1__["isEmpty"];
var includes_fn = lodash__WEBPACK_IMPORTED_MODULE_1__["includes"];
var cloneDeep_fn = lodash__WEBPACK_IMPORTED_MODULE_1__["cloneDeep"];
var some_fn = lodash__WEBPACK_IMPORTED_MODULE_1__["some"];

var mapNewProvidersToGivenResponse = function mapNewProvidersToGivenResponse(appointment, existingProvidersUuids, response) {
  return map_fn(appointment.providers, function (provider) {
    if (includes_fn(existingProvidersUuids, provider.uuid)) {
      return {
        uuid: provider.uuid,
        response: provider.response
      };
    } else {
      return {
        uuid: provider.uuid,
        response: response
      };
    }
  });
};

var isStatusRequested = function isStatusRequested(status) {
  return status === appointmentStatusList.Requested;
};

var isStatusScheduled = function isStatusScheduled(status) {
  return status === appointmentStatusList.Scheduled;
};

var isNewAppointment = function isNewAppointment(appointment) {
  return !appointment.uuid;
};

var getStatusForAppointment = function getStatusForAppointment(appointment) {
  if (isNewAppointment(appointment) || isStatusRequested(appointment.status)) {
    return appointmentStatusList.Scheduled;
  } else {
    return appointment.status;
  }
};

var updateIfCurrentProviderInAppointment = function updateIfCurrentProviderInAppointment(statusAndProviderResponse, currentProviderUuid, appointment) {
  var clone = cloneDeep_fn(statusAndProviderResponse);
  var isCurrentProviderInAppointment = some_fn(statusAndProviderResponse.providers, function (provider) {
    return provider.uuid === currentProviderUuid;
  });
  if (!isCurrentProviderInAppointment) return clone;
  clone.status = getStatusForAppointment(appointment);
  clone.providers = map_fn(clone.providers, function (provider) {
    var response = provider.uuid === currentProviderUuid ? providerResponseList.ACCEPTED : provider.response;
    return {
      uuid: provider.uuid,
      response: response
    };
  });
  return clone;
};

var updateIfRescheduled = function updateIfRescheduled(statusAndProviderResponse, appointment, currentProviderUuid) {
  // in this case we don't keep the existing appointment status and responses
  //this is an special edit
  var clone = cloneDeep_fn(statusAndProviderResponse);
  var isCurrentProviderInAppointment = some_fn(clone.providers, function (provider) {
    return provider.uuid === currentProviderUuid;
  });
  clone.status = isCurrentProviderInAppointment ? appointmentStatusList.Scheduled : appointmentStatusList.Requested;
  clone.providers = map_fn(clone.providers, function (provider) {
    var response = provider.uuid === currentProviderUuid ? providerResponseList.ACCEPTED : providerResponseList.AWAITING;
    return {
      uuid: provider.uuid,
      response: response
    };
  });
  return clone;
};

var updateIfAtleastOneProviderHasAccepted = function updateIfAtleastOneProviderHasAccepted(statusAndProviderResponse) {
  //this handles special cases like,
  //  when new providers are added to a no provider appointment
  //  when only accepted provider is removed from appointment appointment
  var clone = cloneDeep_fn(statusAndProviderResponse);
  var hasAtleastOneAccept = some_fn(clone.providers, function (provider) {
    return provider.response === providerResponseList.ACCEPTED;
  });

  if (hasAtleastOneAccept) {
    if (isStatusRequested(clone.status)) {
      clone.status = appointmentStatusList.Scheduled;
    }
  } else {
    if (isStatusScheduled(clone.status)) {
      clone.status = appointmentStatusList.Requested;
    }
  }

  return clone;
};

var statusAndResponseForScheduledServices = function statusAndResponseForScheduledServices(appointment) {
  var statusAndProviderResponse = {};
  statusAndProviderResponse.status = isNewAppointment(appointment) ? appointmentStatusList.Scheduled : appointment.status;
  statusAndProviderResponse.providers = map_fn(appointment.providers, function (provider) {
    return {
      uuid: provider.uuid,
      response: providerResponseList.ACCEPTED
    };
  });
  return statusAndProviderResponse;
};

var statusAndResponseForRequestedServices = function statusAndResponseForRequestedServices(appointment, existingProvidersUuids) {
  var statusAndProviderResponse = {};
  statusAndProviderResponse.status = isNewAppointment(appointment) ? appointmentStatusList.Requested : appointment.status;
  statusAndProviderResponse.providers = mapNewProvidersToGivenResponse(appointment, existingProvidersUuids, providerResponseList.AWAITING);
  return statusAndProviderResponse;
};

var getUpdatedStatusAndProviderResponse = function getUpdatedStatusAndProviderResponse(appointment, currentProviderUuid, existingProvidersUuids, isRescheduled) {
  if (!isStatusRequested(appointment.service.initialAppointmentStatus)) {
    return statusAndResponseForScheduledServices(appointment);
  }

  if (isEmpty_fn(appointment.providers)) {
    return {
      status: getStatusForAppointment(appointment),
      providers: []
    };
  }

  var statusAndProviderResponse = statusAndResponseForRequestedServices(appointment, existingProvidersUuids);
  statusAndProviderResponse = updateIfCurrentProviderInAppointment(statusAndProviderResponse, currentProviderUuid, appointment);
  statusAndProviderResponse = updateIfAtleastOneProviderHasAccepted(statusAndProviderResponse);

  if (isRescheduled) {
    statusAndProviderResponse = updateIfRescheduled(statusAndProviderResponse, appointment, currentProviderUuid);
  }

  return statusAndProviderResponse;
};

/* harmony default export */ __webpack_exports__["default"] = (getUpdatedStatusAndProviderResponse);

/***/ })

}]);