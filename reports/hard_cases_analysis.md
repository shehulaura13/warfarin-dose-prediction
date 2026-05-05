 Hard-Case Analysis

### Definition

Hard cases are defined as the top 20% of patients with the highest absolute prediction error (n = 222).

---

### Performance

- Overall MAE: 9.44 mg/week 
- Hard-case MAE: 24.46 mg/week

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
| UNKNOWN | 41.4 | 24.6 | +16.8 |
| GG | 31.9 | 19.0 | +12.9 |
| AG | 19.8 | 24.7 | -4.9 |
| AA | 6.8 | 31.6 | -24.8 |

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

### Feature Engineering Attempt

Additional interaction features (e.g., weight × VKORC1 UNKNOWN) were introduced to address error patterns.

Result: 
Model performance deteriorated, indicating overfitting or noise amplification.

These features were subsequently remove
