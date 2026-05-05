SHAP Analysis

SHAP (SHapley Additive exPlanations) was used to interpret model predictions and validate clinical consistency.

---

### Global Feature Effects

#### VKORC1 Genotype

| Genotype | Mean SHAP Value | Interpretation |
|----------|---------------|----------------|
| AA | -6.30 | Strong dose reduction |
| AG | -0.52 | Mild reduction |
| GG | +6.43 | Increased dose requirement |

---

#### CYP2C9 Activity Score

| Activity Score | Genotype | Mean SHAP | Interpretation |
|---------------|----------|----------|----------------|
| 0.0 | *3/*3 | -14.56 | Very low metabolism → strong dose reduction |
| 0.5 | *2/*3 | -14.36 | Reduced metabolism |
| 1.0 | *1/*3, *2/*2 | -7.41 | Moderate reduction |
| 1.5 | *1/*2 | -2.48 | Mild reduction |
| 2.0 | *1/*1 | +1.64 | Normal metabolism → higher dose |

---

#### Drug Interaction Effects

- Amiodarone: -3.77 → reduces dose 
- Amiodarone + VKORC1 AA: -9.9 → strong combined effect 

---

### Clinical Interpretation

The model captures known pharmacogenetic relationships:

- VKORC1 polymorphism affects warfarin sensitivity 
- CYP2C9 variants reduce metabolic clearance 
- Drug interactions (e.g., amiodarone) further decrease dose requirements 

These findings align with established pharmacogenomic guidelines.

---

### Data Limitation

No patients in the test set exhibited the combination:

- VKORC1 AA + CYP2C9 *3/*3 

Implication: 
The model’s behavior in extreme sensitivity scenarios remains unvalidated.

---

### Conclusion

SHAP analysis confirms that the model is:

- Clinically interpretable 
- Mechanistically consistent 
- Sensitive to pharmacogenetic variation 

However, reliability is limited in underrepresented genetic profil
