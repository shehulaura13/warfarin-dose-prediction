 📊 Subgroup Analysis

### Dose Category Performance

The model demonstrates strong performance in the medium-dose range (21–49 mg/week), with 89% of patients correctly classified. However, performance degrades in extreme dosing groups:

- Low-dose patients (<21 mg/week): Frequently overestimated 
- High-dose patients (>49 mg/week): Systematically underestimated 

This indicates regression toward the mean, a common issue in clinical prediction models.

---

### High-Dose Subgroup (>49 mg/week)

High-dose patients are characterized by:

- High prevalence of **CYP2C9 1/1 (normal metabolism) 
- Enrichment of VKORC1 GG (dose resistance) 
- Significant proportion of missing VKORC1 data

Despite genetic profiles suggesting higher dose requirements, the model underpredicts dosing in this group.

Interpretation: 
This bias is likely driven by missing or incomplete genetic information, leading to conservative predictions.

---

### Subgroup Performance Summary

| Group | N | MAE | Within-20% |
|------|----|-----|------------|
| Overall | 1106 | 9.45 | 42.9% |
| Age ≥80 | 133 | 6.71 | 48.1% |
| CYP2C9 *3/*3 | 4 | 6.75 | 25.0% |
| CYP2C9 *1/*1 | 821 | 9.84 | 43.6% |
| BMI 30–40 | 186 | 11.25 | 47.8% |
| Amiodarone | 86 | 7.84 | 48.8% |
| VKORC1 AA | 294 | 5.95 | 43.9% |
| VKORC1 UNKNOWN | 310 | 11.12 | 35.8% |
| VKORC1 GG | 239 | 12.33 | 46.0% |

---

### Key Observations

- Highest error observed in:
  - BMI 30–40
  - VKORC1 GG (resistant patients)
  - Missing VKORC1 genotype

- Model performs best in:
  - Genetically well-characterized patients (e.g., VKORC1 AA)

---

### Drug Representation Limitation

Several clinically relevant medications are underrepresented:

- Fluconazole: 1 patient 
- Rifampin: 1 patient 
- Carbamazepine: 6 patients 

Implication: 
The model is unable to reliably learn interaction effects for these drugs, limiting generalizability.

---

### Race and Genotype Distribution

Genotype frequencies vary significantly across populations:

- VKORC1 AA is more prevalent in Asian populations → associated with lower dose requirements 
- VKORC1 GG is more common in Black and White populations → associated with higher doses 
- **CYP2C9 1/1 dominates across all groups 

Conclusion: 
Observed SHAP patterns are consistent with known population-level pharmacogenetic distributions.


