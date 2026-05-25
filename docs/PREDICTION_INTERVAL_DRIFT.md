# Prediction Interval Drift

## Observation

Prediction interval widths increased substantially
for high-dose patients (>49 mg/week).

Observed:
- larger residuals
- wider conformal intervals
- increased refusal rate

---

## Root Causes

### 1. Dataset Imbalance

High-dose patients underrepresented.

### 2. Missing VKORC1

Many resistant patients lacked genotype information.

### 3. Anthropometric Extremes

Weight and BMI strongly associated with hard-case errors.

---

## Consequence

The uncertainty model correctly learned:
- these patients are difficult

Therefore:
- uncertainty increased
- conformal intervals widened

---

## Important Insight

Wide intervals are NOT necessarily failure.

They may represent:
- honest uncertainty
- correct risk estimation
- clinically appropriate caution

---

## Engineering Tradeoff

Narrow intervals:
- clinically attractive
- often overconfident

Wide intervals:
- safer
- more realistic
- lower refusal rate

This project prioritizes:
- calibrated uncertainty
- safety over overconfidence

