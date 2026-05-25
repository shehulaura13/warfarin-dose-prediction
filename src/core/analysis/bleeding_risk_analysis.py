import pandas as pd
import numpy as np
from src.utils.config import RESULTS_VERSION


# ==============================
# 1. HAS-BLED SCORE
# ==============================
def compute_has_bled(X):
    return (
        (X.get("hypertension", 0)).astype(int) +
        (X["age_decade"] > 6).astype(int) +
        (X.get("stroke", 0)).astype(int) +
        (X.get("renal_failure", 0)).astype(int) +
        (X.get("liver_disease", 0)).astype(int) +
        (X.get("aspirin", 0).fillna(0)).astype(int) +
        (X.get("ibuprofen", 0).fillna(0)).astype(int)
    )


# ==============================
# 2. BUILD CLINICAL DATAFRAME
# ==============================
def build_clinical_dataframe(X_test,y_true, y_pred):

    df = pd.DataFrame()  

   
    df["y_true"] = y_true.values
    df["y_pred"] = y_pred
    needed_cols = [

        "hypertension", "age_decade",

        "stroke", "renal_failure",

        "liver_disease", "aspirin", "ibuprofen"

    ]

    for col in needed_cols:

        if col in X_test.columns:

            df[col] = X_test[col].values

        else:

            df[col] = 0


    # Clinical risk
    # --------------------------
    df["has_bled"] = compute_has_bled(df)
    df["clinical_risk"] = (df["has_bled"] >= 3).astype(int)

    # --------------------------
    # Prediction error
    # --------------------------
    df["relative_error"] = (df["y_pred"] - df["y_true"]) / df["y_true"]

    # --------------------------
    # Dosing classification
    # --------------------------
    df["dosing"] = "safe"

    df.loc[df["relative_error"] > 0.3, "dosing"] = "high_overdose"
    df.loc[(df["relative_error"] > 0.2) & (df["relative_error"] <= 0.3), "dosing"] = "overdose"
    df.loc[(df["relative_error"] > 0.1) & (df["relative_error"] <= 0.2), "dosing"] = "moderate_overdose"

    df.loc[df["relative_error"] < -0.3, "dosing"] = "high_underdose"
    df.loc[(df["relative_error"] < -0.2) & (df["relative_error"] >= -0.3), "dosing"] = "underdose"
    df.loc[(df["relative_error"] < -0.1) & (df["relative_error"] >= -0.2), "dosing"] = "moderate_underdose"

# --- Clinical outcome ---
    df["clinical_outcome"] = "SAFE"

    df.loc[df["dosing"] == "moderate_underdose", "clinical_outcome"] = "MODERATE_CLOTTING_RISK"
    df.loc[df["dosing"] == "underdose", "clinical_outcome"] = "CLOTTING_RISK"
    df.loc[df["dosing"] == "high_underdose", "clinical_outcome"] = "HIGH_CLOTTING_RISK"

    df.loc[df["dosing"] == "moderate_overdose", "clinical_outcome"] = "MODERATE_BLEEDING_RISK"
    df.loc[df["dosing"] == "overdose", "clinical_outcome"] = "BLEEDING_RISK"
    df.loc[df["dosing"] == "high_overdose", "clinical_outcome"] = "HIGH_BLEEDING_RISK"

# --- HAS-BLED override ---
    df.loc[
    (df["clinical_risk"] == 1) & (df["dosing"].isin(["overdose", "moderate_overdose"])),
    "clinical_outcome"
] = "HIGH_BLEEDING_RISK"

   
  

   
    final_cols = [
        "y_true",
        "y_pred",
        "relative_error",
        "dosing",
        "has_bled",
        "clinical_risk",
        "clinical_outcome"
        ]

    df = df[final_cols]

    return df



def run_clinical_analysis(X_test,y_true, y_pred):

    df = build_clinical_dataframe(X_test,y_true, y_pred)

    print("\n=== Clinical Outcome Distribution ===")
    print(df["clinical_outcome"].value_counts(normalize=True))

 
   
    df.to_csv(RESULTS_VERSION/"bleeding_risk_analysis.csv", index=False)

    return df

