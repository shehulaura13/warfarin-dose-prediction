
# MODEL CARD

## Model Details

Model Name: WARFARIN IWPC PROJECT
Version: 1.2.0 
Architecture: XGBoost Regressor + Residual Uncertainty Model 
Framework: scikit-learn + XGBoost + FastAPI 
Developer: LAURA SHEHAJ 
License: Research Use Only (MIT LICENSE )

---

# Intended Use

Clinical decision support prototype for estimating stable weekly warfarin dose.

NOT intended for:
- autonomous prescribing
- pediatric patients
- pregnancy
- severe liver disease
- unsupported CYP2C9 variants

---

# Dataset

Source:
International Warfarin Pharmacogenetics Consortium (IWPC)

Total Patients:
5528

Splits:
- Train: 3316
- Calibration: 1106
- Test: 1106

Calibration set used exclusively for conformal uncertainty calibration.

---

# Features

## Clinical
- age
- BMI
- weight
- height
- race
- smoking
- comorbidities

## Genetics
- VKORC1
- CYP2C9

## Medications
- amiodarone
- simvastatin
- carbamazepine
- aspirin
- azoles
- phenytoin
- ibuprofen
- rifampin

---

# Main Model

XGBoost hyperparameters:

- max_depth=6
- n_estimators=100
- learning_rate=0.03
- subsample=1
- colsample_bytree=0.7

---

# Uncertainty Modeling

Residual-based heteroscedastic uncertainty estimation.

Pipeline:
1. Generate OOF predictions
2. Compute residuals
3. Train secondary XGBoost:
   X → expected residual
4. Apply conformal calibration

Final interval:

prediction ± q90 × uncertainty

---

# Conformal Calibration

| Metric | Value |
|---|---|
| q90 | 2.93 |
| Coverage | 92.1% |
| Refusal Rate | 13.1% |
| Median PI Width | 36.1 mg/week |

Refusal rule:
- refuse if interval width >50 mg/week

---

# Performance

| Metric | XGBoost |
|---|---|
| MAE | 9.64 mg/week |
| Within-20% Accuracy | 41.8% |
| High-Risk MAE | 7.81 |

---

# Failure Modes

Higher error observed in:
- BMI extremes
- VKORC1 missing
- VKORC1 GG
- high-dose patients


---

# Safety Features

- CPIC-inspired overrides
- uncertainty intervals
- confidence scoring
- prediction refusal
- dose capping
- SHAP explanations
- OOD detection

---

# Ethical Considerations

Known limitations:
- dataset imbalance
- missing genetics
- ancestry bias
- no INR feedback loop
- static prediction

Wide intervals may represent:
- biologic variability
- unmeasured confounding
- missing genotype information
- outliers

---

# Regulatory Status

Research prototype only.

NOT:
- FDA approved
- CE marked
- clinically validated
