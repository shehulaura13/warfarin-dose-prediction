# CPIC Override Logic - Warfarin v1.1.0

## Purpose
Per CPIC Guideline 2017, CYP2C9 variants alter warfarin metabolism. CPIC provides MAXIMUM recommended starting doses before considering clinical factors.

ML models are not validated for rare genotypes due to data scarcity N<30.

## CPIC Maximum Doses - Hard Ceilings
These are MAX doses before age, VKORC1, drugs, weight. Actual safe dose is often lower.

| Genotype | CPIC Max Dose | ML Behavior | System Action |
| --- | --- | --- | --- |
| CYP2C9 *1/*1 | No max specified | Use ML prediction | None |
| CYP2C9 *1/*2 | ~45 mg/week | Use ML prediction | None |
| CYP2C9 *1/*3 | ~35 mg/week | Use ML prediction | **Soft warning if ML >35** |
| CYP2C9 *2/*2 | ~30 mg/week | Use ML prediction | **Soft warning if ML >30** |
| CYP2C9 *2/*3 | ~30 mg/week | Use ML prediction | **Soft warning if ML >30** |
| CYP2C9 *3/*3 | **20 mg/week** | **DISABLE ML** | **HARD GATE: Return 20mg,not validated,only 4 patients in test set,75% error rate, block ML** |

## Logic Definition

**Hard Gate (*3/*3 only)**:
1. Runs BEFORE model.predict()
2. If CYP2C9 == "*3/*3", return dose_mg_per_week=20.0
3. Set confidence="low", confidence_score=0.0, raw_model_dose=0.0
4. ML model is never called. No exceptions.

**Soft Warning (*1/*3, *2/*2, *2/*3)**:
1. Run ML model normally
2. After prediction, if dose > CPIC max for that genotype, append warning
3. Return ML dose + warning. Do NOT cap dose. Clinician decides.

## High-Risk Combination Flag
The following combination triggers:
`contraindicated_combo`
Criteria:
- Age ≥70
- Amiodarone present
- CYP2C9 poor metabolizer
Recommended action:
- start conservative dosing
- INR monitoring within 72h
- clinician review required

## Limitations
1. **N<30 for rarest variants**(*1/*5,*1/*6,*1/*11,*1/*13,*1/*14): Model not validated on these genotypes.
2. **Age/Drugs/VKORC1 not in table**: CPIC max must be further reduced by clinical factors. Model attempts this but may fail.
3. **Validation**: *3/*3 N=4, Clinical Accuracy 25%. Hard gate enforced due to insufficient safety data.


