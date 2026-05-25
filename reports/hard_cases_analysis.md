 Hard-Case Analysis

### Definition

Hard cases are defined as the top 20% of patients with the highest absolute prediction error (n = 222).

---

### Performance

- Overall MAE: 9.64 mg/week 
- Hard-case MAE: 24.72mg/week

This represents a substantial degradation in predictive accuracy.

---

### Drivers of Error

Feature importance within hard cases indicates:

| Feature | Contribution to Error |
|--------|----------------------|
| Weight (kg) | High |
| Height (cm) | Moderate |
| BMI | Moderate |

Interpretation: 
Anthropometric variables disproportionately contribute to prediction error in difficult cases, suggesting that non-linear or unmodeled physiological factors may be involved.

---

### Genetic Distribution in Hard Cases

| VKORC1 | Hard (%) | Easy (%) | Difference |
|--------|---------|---------|-----------|
| UNKNOWN | 42.3 | 24.4 | +17.9 |
| GG | 31.5 | 19.1 | +12.4 |
| AG | 19.8 | 24.7 | -4.9 |
| AA | 6.3 | 31.6 | -25.3 |

---

### Key Findings

- Hard cases are enriched for:
  - Missing VKORC1 genotype
  - Resistant patients (VKORC1 GG)

- Underrepresented in:
  - VKORC1 AA (sensitive patients)

---

### Model Behavior

The model struggles when:
- Genetic information is missing or incomplete 
- Patients exhibit resistance phenotypes 
- Anthropometric signals dominate genetic signals 


---
Conclusion

- Model tends to predict VKORC1 UNKNOWN genotype as VKORC1 GG  Warfarin resistant type in hard cases
- Model tends to overpredict low dosed patients and underpredict high dosed patients,confirming model overall biased behaviour towards mean