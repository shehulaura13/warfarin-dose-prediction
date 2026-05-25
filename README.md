 Warfarin Dose Prediction – Clinical AI System

End-to-end clinical machine learning system for personalized warfarin dosing, integrating pharmacogenomics, explainability, and production-ready deployment via FastAPI.

Performance: 21% MAE reduction vs IWPC clinical algorithm 
Status: Research prototype (not for clinical use)

---

Disclaimer
This system is intended for research and educational purposes only. 
Not approved for clinical use. Requires prospective validation before deployment in healthcare settings.

---

Clinical Impact

| Metric | IWPC Clinical | XGBoost Model | Improvement |
|--------|-------------|--------------|------------|
| MAE (mg/week) | 11.97 | 9.44 | -21.1% |
| Within-20% Accuracy | 16.2% | 42.8% | +62.1% |
| High-Risk MAE (age ≥70 or amiodarone) | 10.85 | 7.21 | -33.5% |
| Hard Cases MAE (top 20% errors) | 25.22 | 24.46 | ~no improvement |

---

Critical Findings

- Model performance is highly sensitive to rare genotypes
- Inclusion of CYP2C9 *3/*3 patients increases MAE:
  - 8.66 → 9.44
- Indicates poor generalization to underrepresented pharmacogenetic profiles

Conclusion: 
The model outperforms IWPC overall, but performance degrades in rare and high-risk cases, which are clinically critical.

---

Dataset

- Source: IWPC (International Warfarin Pharmacogenetics Consortium)
- Size: ~5000 patients 
- Test set: ~1100 patients 
- Target: Stable therapeutic weekly dose

Key Data Challenges
- Missing VKORC1 and CYP2C9 genotypes 
- Severe imbalance in rare variants (*3/*3) 
- Limited representation of drug interactions 

---

Feature Engineering

Clinical Features
- Age → encoded as decades 
- Weight, height → BMI 
- Race 
- Comorbidities (CHF, diabetes, hypertension, valve replacement)

Pharmacogenomics
- VKORC1 (-1639 G>A):
  - AA → sensitive (low dose)
  - AG → intermediate
  - GG → resistant (high dose)
  - UNKNOWN → treated as category

- CYP2C9 Activity Score:
  - *1/*1 → 2.0 (normal metabolism)
  - *3/*3 → 0.0 (poor metabolism)

Medications
- Amiodarone (strong inhibitor → ↓ dose)
- Carbamazepine (inducer → ↑ dose)
- Azoles, aspirin (limited representation)

---

Models

- IWPC Clinical Algorithm (baseline)
- Linear Regression
- Random Forest
- XGBoost (selected)

Training Strategy
- GroupShuffleSplit → prevents patient leakage 
- Hyperparameter tuning 
- Feature selection based on clinical relevance 

---

Explainability (SHAP)

Key Drivers of Dose

- VKORC1 AA → strong dose reduction
- CYP2C9 variants → reduced metabolism → lower dose
- Age → older patients require lower dose
- Weight → higher weight → higher dose
- Amiodarone → decreases dose

Clinical Validation
Model behavior aligns with known pharmacogenetic mechanisms and CPIC guidelines:
- VKORC1 affects warfarin sensitivity 
- CYP2C9 affects drug metabolism 

---

Failure Analysis

Hard Cases (Top 20% Errors)
- MAE: 24.46 vs 9.44 overall

Main Drivers of Error
- Weight / BMI (dominant)
- Missing VKORC1 genotype
- Resistant patients (VKORC1 GG)

Insight: 
Anthropometric features dominate error in difficult cases, suggesting missing biological or lifestyle variables.

---

Subgroup Insights

High-Dose Patients (>49 mg/week)
- Frequently underpredicted
- Enriched with:
  - CYP2C9 *1/*1
  - VKORC1 GG / UNKNOWN

Cause: Missing genetic data → systematic underestimation bias

High-Error Groups
- BMI 30–40
- VKORC1 GG
- VKORC1 UNKNOWN

---

System Architecture

Clinical Input → FastAPI Validation → Feature Engineering → 
Sklearn Pipeline (Preprocessing + XGBoost) → 
Post-processing (uncertainty, flags, SHAP) → JSON Output

---

Safety & Reliability

- Uncertainty estimation (tree dropout)
- Out-of-distribution detection
- Clinical flags (high-risk patients)
- Dose caps for missing genetics

---

API Example

Request
json {   "age": "80-89",   "race": "White",   "weight_kg": 75,   "height_cm": 170,   "vkorc1": "AG",   "cyp2c9": "*1/*2",   "amiodarone": 1 }

Response
json {   "dose_mg_per_week": 24.5,   "uncertainty_std": 3.2,   "confidence": "medium",   "flags": ["elderly_high_risk"],   "clinical_summary": "...",   "shap_explanations": {...} }

---

Evaluation

- MAE 
- Within-20% accuracy 
- Dose category accuracy 
- Subgroup analysis 
- Hard-case analysis 

---

Limitations

- Missing genetic data (VKORC1, CYP2C9)
- Poor representation of rare genotypes
- Dataset bias (European ancestry dominance)
- No INR feedback loop (static prediction)
- Limited drug interaction data

---

Future Work

- Conformal prediction (uncertainty calibration)
- External validation (UK Biobank, eMERGE)
- EHR integration (FHIR / Epic / Cerner)
- Drift monitoring
- Causal inference (drug effects)

---

Author

LAURA SHEHAJ 
Clinical AI / ML Engineer

