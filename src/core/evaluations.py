import numpy as np
import pandas as pd


#1 MAE,WITHIN20% OF TRUE DOSE,UNDERDOSE RATE,OVERDOSE RATE

def clinical_metrics(y_true, y_pred):

    mae = np.mean(np.abs(y_true-y_pred))

    #Relative error within 20%

    within_20 =np.mean(np.abs(y_pred-y_true)<=0.2*y_true)

    # Over / Under dosing
    underdose = (y_pred < 0.8*y_true).mean()
    overdose = (y_pred > 1.2*y_true).mean()

    return {
        "MAE": mae,
        "Within20": within_20,
        "Underdose_rate": underdose,
        "Overdose_rate": overdose
    }

# -----------------------------
# 2. DOSE CATEGORY ANALYSIS
# -----------------------------
def dose_category_analysis(y_true, y_pred):

    def categorize(dose):
        if dose < 21:
            return "low"
        elif  dose <= 49:
            return "medium"
        else:
            return "high"

    true_cat = pd.Series(y_true).apply(categorize)
    pred_cat = pd.Series(y_pred).apply(categorize)

    acc = (true_cat.values == pred_cat.values).mean()

    return {
        "Dose_category_accuracy": acc
    }

# -----------------------------
# 3. HIGH-RISK SUBGROUP
# -----------------------------
def evaluate_high_risk(X_test, y_true, y_pred):
   
    high_risk_mask =(
        (X_test['age_decade'] > 7) |
        (X_test["amiodarone"] == 1)
    )

    if high_risk_mask.sum() == 0:
        return {"HighRisk_note": "No patients found"}

    y_true_hr = y_true[high_risk_mask]
    y_pred_hr = y_pred[high_risk_mask]

    return clinical_metrics(y_true_hr, y_pred_hr)

# -----------------------------
# 4. HARD CASES (TOP 20% ERROR)
# -----------------------------
def evaluate_hard_cases(y_true, y_pred):

    errors = np.abs(y_pred - y_true)
    
    threshold = np.percentile(errors, 80)

    hard_mask = errors >= threshold
    

    return {
        "Hard_cases_count": hard_mask.sum(),
        "Hard_cases_MAE": errors[hard_mask].mean()
    }

# -----------------------------
# 5. FULL CLINICAL REPORT
# -----------------------------
def full_clinical_evaluation(model_name, X_test, y_test, y_pred):

    results = {}

    # Basic
    results.update(clinical_metrics(y_test, y_pred))

    # Dose categories
    results.update(dose_category_analysis(y_test, y_pred))

    # High risk
    hr = evaluate_high_risk(X_test, y_test, y_pred)
    results.update({f"HR_{k}": v for k, v in hr.items()})

    # Hard cases
    results.update(evaluate_hard_cases(y_test, y_pred))

    results["model"] = model_name

    return results




