# Validation Plan

## Current Validation

Performed:
- holdout test evaluation
- subgroup analysis
- hard-case analysis
- bleeding-risk analysis
- shap analysis
- conformal calibration
- uncertainty evaluation

---

## Required Future Validation

### 1. External Cohorts

Validate on:
- eMERGE
- UK Biobank
- hospital EHR cohorts

---

## 2. Temporal Validation

Evaluate:
- robustness across time
- genotype prevalence drift
- prescribing drift

---

## 3. Fairness Analysis

Assess performance across:
- race
- sex
- age
- genotype groups

---

## 4. Clinical Simulation

Simulate:
- INR titration workflows
- overdose prevention
- bleeding risk reduction

---

## 5. Prospective Validation

Required before deployment:
- clinician oversight
- IRB approval
- safety monitoring

---

## 6. Improvements
- Sequential model or Adaptive dosing systems
- Hierarchial modeling
- Multimodel AI (integrating EHR data & NLP)


## Success Criteria

Potential clinical-readiness targets:
- >55% within 20%
- calibrated 90% uncertainty coverage
- reduced overdose events
- stable subgroup performance
