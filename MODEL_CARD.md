MODEL DETAILS
Model Name: Warfarin IWPC Dose Predictor v1.0
Model Architecture: XGBoost Regressor
Hyperparameters: max_depth=4, n_estimators=200, learning_rate=0.03
Version: 1.0.0, trained 2026-04-23
Developed by: LAURA SHEHAJ
License: Research Use Only. Not for clinical use without external validation.
Framework: scikit-learn pipeline + XGBoost 2.x, FastAPI 0.115+

INTENDED USE

Primary Intended Users:
Physicians, pharmacists, anticoagulation management services with warfarin dosing privileges.

Out-of-Scope Uses:
1. Pediatric patients <18 years. No training data.
2. Standalone prescribing. Model uncertainty std=3.2-8.66 mg/week requires INR titration.
3. Patients with physiologically impossible inputs: BMI <12 or >60, weight <20kg or >200kg.
   API returns HTTP 422.
4. Pregnancy, severe liver disease, acute illness. Not represented in IWPC cohort.
5. Patients with CYP2C9*5, *6, *11 variants. Not captured in feature set.

TRAINING DATA

Dataset: International Warfarin Pharmacogenetics Consortium (IWPC), n=5,528 patients
Inclusion: Patients with documented stable therapeutic warfarin dose at INR 2-3
Exclusions: Missing target dose. 
Demographics: Age 18-95, 55% Male. Race: 65% White, 20% Asian, 15% Black or African American.
Geography: 21 research groups, 9 countries. US/EU/Asia dominant.
Key Features: 38 after one-hot encoding
    - Demographics: age_decade, gender, race, BMI
    - Genetics: VKORC1-1639G>A (AA/AG/GG), CYP2C9*1/*2/*3 activity score
    - Medications: amiodarone, carbamazepine, rifampin, aspirin
    - Comorbidities: valve_replacement, CHF, diabetes, hypertension
Data Leakage Prevention: Target dose, INR values, and follow-up doses excluded from features.
Missing Data Handling: VKORC1 missing=29.5% treated as 'UNKNOWN'.

EVALUATION DATA + METRICS

Evaluation: Hold-out test set, GroupShuffleSplit by patient to prevent leakage
Sample Size: n=1,106 test patients (20% of 5,528)

Overall Performance:
| Model | MAE (mg/week) | Within-20% Accuracy | High-Risk MAE* |
| --- | --- | --- | --- |
| IWPC Clinical Formula | 11.97 | 16.0% | 10.85 |
| Linear Regression | 9.49 | 41.6% | 7.22 |
| Random Forest | 9.8 | 39.8% | 8.05 |
| **XGBoost (Deployed)** | **9.44** | **42.9%** | **7.21** |
*High-Risk: age≥70 or amiodarone=1

Relative Improvement vs IWPC: 20.1% MAE reduction, 2.6x increase in Within-20% accuracy

Dose Category Accuracy:
Low <21 mg/week: 46%
Medium 21-49 mg/week: 89%
High >49 mg/week: 29%

Error Analysis - Hard Cases (Top 20% MAE, n=222):
- XGBoost MAE: 24.46 mg/week vs IWPC 25.2 mg/week
- Drivers: Weight +9.4kg, BMI +3 above easy cases. Missing VKORC1: 41.4% vs 24.6% in easy cases
- Interpretation: Model fails predictably on extreme physiologic values + missing genotype

Subgroup Performance(in test set(1100 patients)):
| Subgroup | N | MAE (mg/week) | %Within20% | Note |
| --- | --- | --- | --- |
| Age 80+ | 133   6.71 	48.1 | Lower MAE than overall. n=133 limits confidence. Prospective validation required given bleeding risk |
| CYP2C9 *3/*3 |4.0	6.75	25.0 | Only 4 patient representation in test set.not enough data to validate properly
| BMI 30-40 | 186.0	11.25	47.8 | 16% higher MAE vs overall. Aligns with hard-case drivers. Consider wider INR monitoring window |
| Amiodarone | 86.0	7.84	48.8| Performance maintained. Drug interaction learned. Monitor via `contraindicated_combo` if Age 80+ + *3/*3 |
| Vkorc1 UNKNOWN | 310.0	11.12	35.8| Missing vkorc1 genotypes increases Mae.More genetic information required.Flaged in lower confidence score
| Vkorc1 GG | 239.0	12.33	46.0| vkorc1 GG genotypes increases Mae.Flaged in lower confidence score



ETHICAL CONSIDERATIONS,CAVEATS,SAFETY FEATURES

Known Limitations:
1. Small dataset,a lot of null values and not enough features unique values representation
 in training and  mostly test set
2. Dataset Bias: IWPC over-represents European ancestry. Performance on Hispanic,
   Middle Eastern, Indigenous populations not validated. Requires external cohort testing.
3. Missing Data Bias: 29.5% VKORC1 missing. Model treats as 'UNKNOWN' which degrades accuracy.
   Hard-case analysis shows 39.6% of large errors lack VKORC1.
4. Rare Variants: CYP2C9*5, *6, *11 not captured. May significantly underdose carriers.
5. No Temporal Data: Static prediction. Does not incorporate serial INR or dose adjustments.

Quantitative Fairness: Not yet assessed across race/sex. Required before clinical pilot.

Safety Features Implemented in Production API:
1. Input Validation Layer: Pydantic schema blocks BMI <12 or >60, weight <20kg or >200kg
   with HTTP 422. Prevents out-of-distribution physiologic inputs.
2. Clinical Safety Rules: `contraindicated_combo` flag fires for Age≥80 + CYP2C9*3/*3 + amiodarone.
   Returns action: "CRITICAL: Start <15mg/week, check INR day 3".
3. Uncertainty Quantification: Returns `uncertainty_std` and `relative_uncertainty`.
   `confidence` set to 'low' if high_uncertainty, missing_genetics, or contraindicated_combo present.
4. Dose Capping: Raw predictions capped at clinical_max_dose=70 mg/week or 99th percentile
   of training data to prevent extreme outputs.
5. Missing Genetics Handling: `missing_genetics` flag + confidence='low' when VKORC1 or
   CYP2C9 not provided. Prompts clinician to order genotype.

Explainability for Trust:
SHAP values returned via API. Top pharmacologic drivers validated:
- VKORC1 AA: -6.44 mg/week | GG: +6.20 mg/week
- CYP2C9 *3/*3: -11.59 mg/week vs *1/*1
- Weight: +0.12 mg/kg | Age: -0.15 mg/year
Aligns with warfarin PK/PD literature.

Human Oversight Requirements:
1. Output is decision support only. Licensed clinician must review dose, flags, SHAP, and
   confidence before prescribing.
2. Model does not account for dietary vitamin K, acute illness, adherence, or drug
   interactions beyond amiodarone/carbamazepine/rifampin/aspirin(weak signal due to very few patients on these drugs in test set).
3. Mandatory INR monitoring. Model prediction is starting dose only.


Regulatory Status:
Research prototype. Not FDA 510(k) cleared. Not CE marked. Requires IRB approval and
prospective clinical trial before use in patient care per FDA SaMD guidelines.
