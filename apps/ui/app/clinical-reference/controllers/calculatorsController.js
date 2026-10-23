'use strict';

angular.module('bahmni.clinicalReference')
    .controller('CalculatorsController', ['$scope', 'clinicalReferenceService',
        function ($scope, clinicalReferenceService) {
            $scope.calculators = [];
            $scope.selectedCalculator = null;
            $scope.calculatorInput = {};
            $scope.calculatorResult = null;
            $scope.isLoading = false;
            
            clinicalReferenceService.getCalculators().then(function (response) {
                $scope.calculators = response.data.calculators || [];
            });
            
            $scope.selectCalculator = function (calc) {
                $scope.selectedCalculator = calc;
                $scope.calculatorInput = {};
                $scope.calculatorResult = null;
            };
            
            $scope.runCalculator = function () {
                if (!$scope.selectedCalculator) return;
                $scope.isLoading = true;
                clinicalReferenceService.runCalculator($scope.selectedCalculator.id, $scope.calculatorInput).then(function (response) {
                    $scope.calculatorResult = response.data;
                    $scope.isLoading = false;
                }, function (error) {
                    $scope.calculatorResult = null;
                    $scope.isLoading = false;
                });
            };
            
            $scope.goBack = function () {
                $scope.selectedCalculator = null;
                $scope.calculatorResult = null;
            };
            
            $scope.getCategoryColor = function (category) {
                var colors = {
                    'Cardiology': '#e74c3c',
                    'Pulmonology': '#3498db',
                    'Neurology': '#9b59b6',
                    'Critical Care': '#e67e22',
                    'Sepsis': '#c0392b',
                    'Psychiatry': '#1abc9c',
                    'Nephrology': '#2ecc71',
                    'Hepatology': '#f39c12',
                    'Geriatrics': '#95a5a6',
                    'Nursing': '#34495e',
                    'Anthropometry': '#16a085'
                };
                return colors[category] || '#7f8c8d';
            };

            $scope.formatInputLabel = function(input) {
                return (input || '').replace(/_/g, ' ');
            };

            $scope.getInputPlaceholder = function(input) {
                var hints = {
                    'weight_kg': 'e.g. 70 (kg)',
                    'height_m': 'e.g. 1.75 (meters)',
                    'systolic': 'e.g. 120 (mmHg)',
                    'diastolic': 'e.g. 80 (mmHg)',
                    'eye': 'Eye opening: 1 (None) to 4 (Spontaneous)',
                    'verbal': 'Verbal: 1 (None) to 5 (Oriented)',
                    'motor': 'Motor: 1 (None) to 6 (Obeys commands)',
                    'confusion': '1 if Confused, 0 if Normal',
                    'urea': '1 if > 7 mmol/L (19 mg/dL), 0 if Normal',
                    'respiratory_rate': '1 if ≥ 30/min, 0 if < 30',
                    'blood_pressure': '1 if SBP<90 or DBP≤60, 0 if Normal',
                    'age_65plus': '1 if Age ≥ 65, 0 if < 65',
                    'clinical_signs_dvt': '1 if DVT symptoms, 0 if No',
                    'pe_most_likely': '1 if PE #1 diagnosis, 0 if No',
                    'heart_rate': '1 if HR > 100 bpm, 0 if ≤ 100',
                    'immobilization': '1 if Surgery/Bed rest, 0 if No',
                    'previous_pe': '1 if Prior PE/DVT, 0 if No',
                    'hemoptysis': '1 if Coughing blood, 0 if No',
                    'malignancy': '1 if Active cancer, 0 if No',
                    'chf': '1 if Congestive Heart Failure, 0 if No',
                    'hypertension': '1 if Hypertensive, 0 if No',
                    'diabetes': '1 if Diabetic, 0 if No',
                    'stroke': '1 if Prior Stroke/TIA, 0 if No',
                    'vascular_disease': '1 if Prior MI/PAD, 0 if No',
                    'age_75plus': '1 if Age ≥ 75, 0 if No',
                    'age_65_74': '1 if Age 65-74, 0 if No',
                    'female': '1 if Female, 0 if Male',
                    'abnormal_renal': '1 if Renal disease, 0 if No',
                    'abnormal_liver': '1 if Liver disease, 0 if No',
                    'bleeding': '1 if Prior major bleed, 0 if No',
                    'labile_inr': '1 if Labile INR, 0 if No',
                    'elderly': '1 if Age > 65, 0 if No',
                    'drugs': '1 if Antiplatelets/NSAIDs, 0 if No',
                    'alcohol': '1 if Alcohol excess, 0 if No',
                    'altered_mentation': '1 if Altered (GCS<15), 0 if Normal',
                    'systolic_bp': '1 if SBP ≤ 100 mmHg, 0 if > 100',
                    'ascites': '1 (None), 2 (Slight), 3 (Moderate/Severe)',
                    'encephalopathy': '1 (None), 2 (Grade 1-2), 3 (Grade 3-4)',
                    'pao2_fio2': 'Score (0-4) or ratio',
                    'platelets': 'Score (0-4) or count',
                    'creatinine': 'Score (0-4) or level',
                    'bilirubin': 'Score (1-3) or level',
                    'albumin': 'Score (1-3) or level',
                    'inr': 'Score (1-3) or level'
                };
                if (input && input.indexOf('q') === 0) {
                    return '0 (Not at all) to 3 (Nearly every day)';
                }
                return hints[input] || 'Enter ' + (input || '').replace(/_/g, ' ');
            };
        }
    ]);
