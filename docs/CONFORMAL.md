
# Conformal Prediction

## Motivation

Warfarin dosing contains substantial:
- biological variability
- missing genetic information
- noisy clinical measurements

Point predictions alone are insufficient for clinical decision support.

This project implements conformal prediction intervals
to quantify prediction uncertainty.

---

## Method

### Step 1 — Main Dose Model

Train XGBoost model:
X -> dose

---

### Step 2 — Residual Modeling

Generate out-of-fold predictions on training data.

Residuals:
|y_true - y_pred|

Train secondary XGBoost model:
X -> expected residual

This estimates heteroscedastic uncertainty.

---

## Step 3 — Calibration Set

Separate calibration split:
- never used during model training

Compute normalized conformity scores:

score = absolute_error / predicted_uncertainty

---

## Step 4 — q90 Quantile

For 90% target coverage:

q90 = 2.931

---

## Final Prediction Interval

PI:
prediction ± q90 * uncertainty

---

## Refusal Logic

Predictions are refused if:
- interval width >50 mg/week

Reason:
extremely wide intervals are not clinically actionable.

---

## Observed Behavior

High-dose patients:
- larger uncertainty
- larger intervals
- higher refusal rates

This matched:
- hard-case analysis
- subgroup MAE analysis
- SHAP-driven error analysis

---

## Clinical Interpretation

The uncertainty model does NOT predict:
"true biological uncertainty"

It predicts:
"expected model error based on similar patients"

This distinction is critical.