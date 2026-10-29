'use strict';

Bahmni.Clinical.EncounterTransactionMapper = function () {
    var addEditedDiagnoses = function (consultation, diagnosisList) {
        if (consultation.pastDiagnoses) {
            consultation.pastDiagnoses.forEach(function (diagnosis) {
                if (diagnosis.isDirty) {
                    diagnosis.diagnosisDateTime = null;
                    diagnosisList.push(diagnosis);
                }
            });
        }
        if (consultation.savedDiagnosesFromCurrentEncounter) {
            consultation.savedDiagnosesFromCurrentEncounter.forEach(function (diagnosis) {
                if (diagnosis.isDirty) {
                    diagnosis.diagnosisDateTime = null;
                    diagnosisList.push(diagnosis);
                }
            });
        }
    };

    this.map = function (consultation, patient, locationUuid, retrospectiveEntry, defaultRetrospectiveVisitType, defaultVisitType, isInEditEncounterMode, patientProgramUuid) {
        var encounterData = {};
        encounterData.locationUuid = isInEditEncounterMode ? consultation.locationUuid : locationUuid;
        encounterData.patientUuid = patient.uuid;
        encounterData.encounterUuid = consultation.encounterUuid;
        encounterData.visitUuid = consultation.visitUuid;
        encounterData.providers = consultation.providers;
        encounterData.encounterDateTime = consultation.encounterDateTime;
        encounterData.extensions = {mdrtbSpecimen: consultation.newlyAddedSpecimens};
        encounterData.context = {patientProgramUuid: patientProgramUuid};

        if (!_.isEmpty(retrospectiveEntry)) {
            encounterData.visitType = defaultRetrospectiveVisitType || "OPD";
        } else if (!encounterData.visitUuid) {
            encounterData.visitType = defaultVisitType;
        } else if (!encounterData.visitType) {
            encounterData.visitType = defaultVisitType;
        }

        if (consultation.newlyAddedDiagnoses && consultation.newlyAddedDiagnoses.length > 0) {
            encounterData.bahmniDiagnoses = consultation.newlyAddedDiagnoses.map(function (diagnosis) {
                var conceptSystem = diagnosis.codedAnswer.conceptSystem ? diagnosis.codedAnswer.conceptSystem + "/" : "";
                var comments = diagnosis.comments || "";
                if (diagnosis.icd11Code || diagnosis.diagnosisOccurrence) {
                    var parts = [];
                    if (diagnosis.icd11Code) parts.push("[ICD11:" + diagnosis.icd11Code + "]");
                    if (diagnosis.diagnosisOccurrence) parts.push("[OCC:" + diagnosis.diagnosisOccurrence + "]");
                    comments = parts.join("") + (comments ? " " + comments : "");
                }
                var diagOrder = diagnosis.order;
                if (consultation.mainDiagnosis && consultation.mainDiagnosis.uuid && diagOrder === "PRIMARY") {
                    diagOrder = "SECONDARY";
                }
                return {
                    codedAnswer: { uuid: !diagnosis.isNonCodedAnswer ? conceptSystem + diagnosis.codedAnswer.uuid : undefined},
                    freeTextAnswer: diagnosis.isNonCodedAnswer ? diagnosis.codedAnswer.name : undefined,
                    order: diagOrder,
                    certainty: diagnosis.certainty,
                    existingObs: null,
                    diagnosisDateTime: null,
                    diagnosisStatusConcept: diagnosis.diagnosisStatusConcept,
                    voided: diagnosis.voided,
                    comments: comments
                };
            });
        } else {
            encounterData.bahmniDiagnoses = [];
        }

        if (consultation.mainDiagnosis && consultation.mainDiagnosis.uuid) {
            var mainConceptSystem = consultation.mainDiagnosis.conceptSystem ? consultation.mainDiagnosis.conceptSystem + "/" : "";
            var mainUuid = mainConceptSystem + consultation.mainDiagnosis.uuid;
            var mainComments = "";
            if (consultation.mainDiagnosis.icd11Code || consultation.mainDiagnosis.occurrence) {
                var parts = [];
                if (consultation.mainDiagnosis.icd11Code) parts.push("[ICD11:" + consultation.mainDiagnosis.icd11Code + "]");
                if (consultation.mainDiagnosis.occurrence) parts.push("[OCC:" + consultation.mainDiagnosis.occurrence + "]");
                mainComments = parts.join("");
            }
            var mainDiag = {
                codedAnswer: { uuid: mainUuid },
                freeTextAnswer: undefined,
                order: "PRIMARY",
                certainty: "CONFIRMED",
                existingObs: null,
                diagnosisDateTime: null,
                diagnosisStatusConcept: null,
                voided: false,
                comments: mainComments
            };
            var isDuplicate = encounterData.bahmniDiagnoses.some(function (d) {
                return d.codedAnswer && d.codedAnswer.uuid && d.codedAnswer.uuid === mainDiag.codedAnswer.uuid;
            });
            if (!isDuplicate) {
                encounterData.bahmniDiagnoses.unshift(mainDiag);
            }
        }
        addEditedDiagnoses(consultation, encounterData.bahmniDiagnoses);
        encounterData.orders = [];
        var addOrdersToEncounter = function () {
            var modifiedOrders = _.filter(consultation.orders, function (order) {
                var ordUuid = order.concept ? order.concept.uuid : order.uuid;
                var isStockOut = order.isUnavailable ||
                                 (order.concept && order.concept.isUnavailable) ||
                                 (consultation.referralOrders && _.some(consultation.referralOrders, function (r) {
                                     return r.uuid === ordUuid || (r.concept && r.concept.uuid === ordUuid);
                                 }));
                if (isStockOut && !order.isDiscontinued) {
                    return false;
                }
                return order.hasBeenModified || order.isDiscontinued || !order.uuid;
            });
            var labConceptClasses = ["Test", "LabSet", "LabTest"];
            var tempOrders = modifiedOrders.map(function (order) {
                order.urgency = order.isUrgent ? "STAT" : undefined;
                var comment = order.commentToFulfiller || '';
                var conceptClassName = order.conceptClassName || (order.concept && order.concept.conceptClass && order.concept.conceptClass.name);
                var orderTypeName = order.orderTypeName || (order.orderType && order.orderType.name);
                var isLabOrder = (conceptClassName && labConceptClasses.indexOf(conceptClassName) !== -1) ||
                                 (orderTypeName && orderTypeName.toLowerCase().indexOf('lab') !== -1);
                if (isLabOrder && consultation.labLocationId && consultation.labLocationName) {
                    var locationTag = '[LAB_LOCATION:' + consultation.labLocationName + ']';
                    if (comment.indexOf('[LAB_LOCATION:') === -1) {
                        comment = locationTag + (comment ? ' ' + comment : '');
                    } else {
                        comment = comment.replace(/\[LAB_LOCATION:[^\]]*\]/, locationTag);
                    }
                }

                if (order.hasBeenModified && !order.isDiscontinued) {
                    var revised = Bahmni.Clinical.Order.revise(order);
                    revised.commentToFulfiller = comment;
                    return revised;
                } else if (order.isDiscontinued) {
                    return Bahmni.Clinical.Order.discontinue(order);
                }
                return { uuid: order.uuid, concept: {name: order.concept.name, uuid: order.concept.uuid },
                    commentToFulfiller: comment, urgency: order.urgency};
            });
            encounterData.orders = encounterData.orders.concat(tempOrders);
        };
        addOrdersToEncounter();

        consultation.drugOrders = [];

        var newlyAddedTreatments = consultation.newlyAddedTreatments;
        if (newlyAddedTreatments) {
            newlyAddedTreatments.forEach(function (treatment) {
                consultation.drugOrders.push(Bahmni.Clinical.DrugOrder.createFromUIObject(treatment));
            });
        }
        if (consultation.removableDrugs) {
            consultation.drugOrders = consultation.drugOrders.concat(consultation.removableDrugs);
        }

        encounterData.drugOrders = consultation.drugOrders;

        encounterData.disposition = consultation.disposition;

        var addObservationsToEncounter = function () {
            encounterData.observations = consultation.observations || [];

            if (consultation.consultationNote) {
                encounterData.observations.push(consultation.consultationNote);
            }
            if (consultation.labOrderNote) {
                encounterData.observations.push(consultation.labOrderNote);
            }
            if (consultation.referralOrders && consultation.referralOrders.length > 0) {
                var labNoteConcept = (consultation.labOrderNote && consultation.labOrderNote.concept) || {
                    uuid: "d3e3f4be-5e07-11ef-8f7c-0242ac120002",
                    name: "Lab Order Notes"
                };
                consultation.referralOrders.forEach(function (ro) {
                    var testName = ro.name || ro.displayName || (ro.concept ? (ro.concept.displayName || ro.concept.name) : 'Test');
                    var obsValue = '[STOCK-OUT: Reagent Unavailable] ' + testName;
                    encounterData.observations.push({
                        concept: labNoteConcept,
                        value: obsValue,
                        comment: 'Stock-Out: Reagent Unavailable',
                        observationDateTime: encounterData.encounterDateTime || null
                    });
                });
            }
            if (!_.isEmpty(consultation.drugOrdersWithUpdatedOrderAttributes)) {
                var orderAttributes = _.values(consultation.drugOrdersWithUpdatedOrderAttributes).map(function (drugOrder) {
                    return drugOrder.getOrderAttributesAsObs();
                });
                encounterData.observations = encounterData.observations.concat(_.flatten(orderAttributes));
            }
        };

        addObservationsToEncounter();

        if (consultation.followUpConditions) {
            [].push.apply(consultation.observations, consultation.followUpConditions);
        }

        return encounterData;
    };
};
