'use strict';

angular.module('bahmni.orders')
    .factory('orderFulfillmentConfig', ['conceptSetService',
        function (conceptSetService) {
            return function (formName) {
                return conceptSetService.getConcept({
                    name: formName,
                    v: Bahmni.Common.Constants.conceptSetRepresentationForOrderFulfillmentConfig
                }).then(function (response) {
                    var config = {};
                    var firstResult = response.data && response.data.results && response.data.results[0];
                    var formMembers = (firstResult && firstResult.setMembers) || [];
                    config.conceptNames = _.map(formMembers, function (concept) {
                        return concept.name ? (concept.name.name || concept.name.display || concept.name) : '';
                    }).filter(Boolean);
                    config.isObservation = true;
                    config.showDetailsButton = true;
                    config.hideIfEmpty = false;
                    config.showHeader = false;
                    config.scope = "latest";
                    return config;
                }, function () {
                    return {
                        conceptNames: [],
                        isObservation: true,
                        showDetailsButton: true,
                        hideIfEmpty: false,
                        showHeader: false,
                        scope: "latest"
                    };
                });
            };
        }
    ]
);
