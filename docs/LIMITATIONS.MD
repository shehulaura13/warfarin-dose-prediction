# LIMITATIONS - Warfarin Dose Prediction v1.0.0


## 1. Dataset Size

The IWPC dataset (~5,500 patients) is relatively small for machine learning,
especially for rare pharmacogenomic subgroups.

Rare CYP2C9 variants:
- *3/*3 represented only 20 total patients
- Test set contained only 4 patients

This prevents reliable estimation of performance in poor metabolizers.

---

## 2. Missing Genetics

VKORC1 genotype missingness:
- ~29.5% of patients

Missing pharmacogenomic information was strongly associated with:
- higher model error
- wider uncertainty intervals
- lower confidence predictions

---

## 3. Population Bias

The IWPC cohort is enriched for:
- European ancestry populations

Performance on:
- Middle Eastern
- Hispanic
- Indigenous
- African populations

requires external validation.

---

## 4. Static Prediction & Missing Covariates

The model predicts:
- initial stable weekly dose only

The system does NOT incorporate:
- serial INR measurements
- INR History
- dynamic titration
- adherence
- dietary vitamin K
- nuanced bedside context


---

## 5. Limited Drug Interaction Representation

Several interacting drugs were rare:
- azoles
- rifampin
- phenytoin
- carbamazepine

The model likely underestimates uncertainty for uncommon medication combinations.

---

## 6. High-Dose Patients

Patients requiring >49 mg/week showed:
- higher MAE
- larger uncertainty intervals
- more frequent refusal

This suggests:
- unmodeled resistance mechanisms
- missing biological variables
- limited representation in training data

---

## 7. Out-of-Scope
1. Patients <18 years, pregnant, liver failure


## 8. Uncertainty
v1.0.0 provides point predictions only. No confidence intervals. 
v1.2.0 provides conformal intervals but sets wider range of width due to heterogenous,heteroscedastic,noisy,missing IWPC dataset

## 9.Comparison
XGBoost outperform IWPC baseline model but suggested comparison with:
- Catboost
- LightGBM
- GAMS
- Bayesian Model

## 10. Research Prototype

This system is:
- NOT FDA approved
- NOT CE marked
- NOT clinically validated prospectively

It should only be used:
- for education
- research
- portfolio demonstration

