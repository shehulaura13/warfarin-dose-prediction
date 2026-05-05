import numpy as np
import pandas as pd
import shap
import xgboost

def compute_uncertainty_xgb(model, X_row_trans, n_boot=30):
   
    # XGBoost
    if hasattr(model, "get_booster"):
        booster = model.get_booster()
        preds = []
        n_trees = model.n_estimators
        for _ in range(n_boot):
            # Predict with random 80% of trees each time
            end_tree = int(n_trees * np.random.uniform(0.7, 1.0))
            pred = booster.predict(xgboost.DMatrix(X_row_trans), iteration_range=(0, end_tree))
            preds.append(pred[0])
        preds = np.array(preds)

    # RandomForest fallback
    elif hasattr(model, "estimators_"):
        preds = np.array([t.predict(X_row_trans)[0] for t in model.estimators_])

    else: # no uncertainty possible
        preds = np.array([model.predict(X_row_trans)[0]])

    mean_pred = preds.mean()
    std_pred = preds.std()
    rel_unc = std_pred / mean_pred if mean_pred > 1e-6 else 0
    return float(mean_pred), float(std_pred), float(rel_unc)



def detect_ood_and_risks(X_row, thresholds, std, dose, patient_dict):
   
    flags = []
    actions = []

    bmi = X_row["bmi"].values[0]
    
    age = X_row["age_decade"].values[0]
    weight = X_row["weight_kg"].values[0]
    height = X_row["height_cm"].values[0] 

    # === IMPOSSIBLE PATIENT TEST ===
   
    if weight < 25 or weight > 250:
        flags.append("impossible_weight")
        actions.append("Weight outside human range")
    

    # === CONTRAINDICATED COMBO
    is_elderly = age >= 8 #age decade
    is_slow_metabolizer = "*3/*3" in str(patient_dict.get("cyp2c9_genotypes", ""))
    on_amiodarone = patient_dict.get("amiodarone", 0) == 1

    if is_elderly and is_slow_metabolizer and on_amiodarone:
        flags.append("contraindicated_combo")
        actions.append("CRITICAL: Elderly + CYP2C9*3/*3 + amiodarone. Start <15mg/week, check INR day 3")

    
    # === MISSING GENETICS ===
    vkorc1 = patient_dict.get("vkorc1_1639")
    cyp2c9 = patient_dict.get("cyp2c9_genotypes")

    if vkorc1 is None or cyp2c9 is None or vkorc1 == "" or cyp2c9 == "":
       flags.append("missing_genetics")
       actions.append("Genotype patient before dosing")

    if is_slow_metabolizer:
        flags.append("poor_metabolizer")
        actions.append("Dose Range:3,5-14mg/week.CPIC Overide.MD review,INR at day 3")

    
    if vkorc1 == "GG":
       flags.append("vkorc1_gg_high_error")  
       actions.append("VKORC1 GG genotype: Warfarin resistant. Model MAE=12.3mg on this group. Recommend INR on days 3, 7, 14.")

    if 30 <= bmi <= 40:  
       flags.append("obese_bmi")  
       actions.append("BMI 30-40: Obese. Model MAE=11.3mg. Consider starting at 90% of predicted dose and titrate with INR.")

    # === OOD: 99th percentile ===
    if bmi > thresholds["bmi_high"]:
        flags.append("extreme_BMI")
        actions.append("Clinical review required: BMI outside training data")
    
    

    if age > thresholds["age_high"]:
        flags.append("elderly_high_risk")
        actions.append("Elderly: consider dose reduction & frequent INR")

    
    # === HIGH UNCERTAINTY ===
    if dose > 0 and (std / dose) > 0.25: # 25% relative std
        flags.append("high_uncertainty")
        actions.append("Model uncertainty high. Do not rely on prediction alone")

    return list(set(flags)), list(set(actions)) 

def generate_clinical_explanations(pipeline, X_row_df, top_n=5):
    
    model = pipeline.named_steps['model']
    preprocessor = pipeline.named_steps['preprocessor']

    explainer = shap.TreeExplainer(model)
    X_trans = preprocessor.transform(X_row_df)
    shap_values = explainer.shap_values(X_trans)

    
    try:
        feature_names = preprocessor.get_feature_names_out()
    except:
        feature_names = X_row_df.columns

    values = shap_values[0]
    data = X_trans[0]
    raw_data = X_row_df.iloc[0].to_dict()

    sorted_idx = np.argsort(np.abs(values))[::-1][:top_n]
    explanations = {}
    sentences = []

    for i in sorted_idx:
        feat = feature_names[i]
        shap_val = values[i]

        raw_feat_name = feat.split('__')[-1]
        raw_val = raw_data.get(raw_feat_name, data[i]) # fallback to transformed

        explanations[feat] = float(shap_val)
        direction = "increases" if shap_val > 0 else "decreases"
        sentences.append(f"{raw_feat_name}={raw_val} {direction} dose by {abs(shap_val):.1f} mg/week")

    clinical_summary = " | ".join(sentences)
    return explanations, clinical_summary

def build_api_response(pipeline, X_row_df,thresholds, patient_dict, clinical_max_dose=70):
   
    model = pipeline.named_steps['model']
    preprocessor = pipeline.named_steps['preprocessor']
    X_row_trans = preprocessor.transform(X_row_df)

   
    dose, std, rel_unc = compute_uncertainty_xgb(model, X_row_trans)

   
    flags, actions = detect_ood_and_risks(X_row_df, thresholds, std, dose, patient_dict)


    safe_cap = min(clinical_max_dose, thresholds["dose_high"])
    dose_capped = min(dose, safe_cap)

    if dose > safe_cap:
        flags.append("dose_capped")
        actions.append(f"Dose capped at {safe_cap:.1f} mg/week for safety")


    explanations, clinical_summary = generate_clinical_explanations(pipeline, X_row_df)

   
    if "high_uncertainty" in flags or "missing_genetics" in flags or "contraindicated_combo" in flags or "is_slow_metabolizer":
        confidence = "low"
    elif "extreme_BMI" in flags or "elderly_high_risk" in flags or "vkorc1_gg_high_error" in flags or "obese_bmi" in flags:
        confidence = "medium"
    else:
        confidence = "high"


    if confidence == "high":
        conf_score = 0.9
    elif confidence == "medium":
        conf_score = 0.6
    else:
        conf_score = 0.3
   

    return {
        "dose_mg_per_week": round(float(dose_capped), 2),
        "raw_model_dose": round(float(dose), 2),
        "uncertainty_std": round(float(std), 2),
        "relative_uncertainty": round(float(rel_unc), 3),
        "confidence": confidence,
        "confidence_score": conf_score,
        "flags": flags,
        "actions": actions,
        "clinical_summary": clinical_summary,
        "shap_explanations": explanations
    }
