import joblib
import pandas as pd
import os
from src.core.config import MODEL_PATH, FEATURES_PATH,MODEL_DIR
from src.features import create_features


_model = None
_feature_cols = None
_thresholds = None
_model_mtime = None

def load_artifacts(force_reload=False):
   
    global _model, _feature_cols, _thresholds, _model_mtime

    current_mtime = os.path.getmtime(MODEL_PATH) if os.path.exists(MODEL_PATH) else 0

    if _model is None or force_reload or current_mtime != _model_mtime:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at: {MODEL_PATH}. Train first.")
        if not os.path.exists(FEATURES_PATH):
            raise FileNotFoundError(f"Features not found at: {FEATURES_PATH}. Run pipeline first.")

        _model = joblib.load(MODEL_PATH)
        _feature_cols = joblib.load(FEATURES_PATH)
        _model_mtime = current_mtime

      #default thresholds
        _thresholds = {
            "dose_high": 60,
            "age_high": 9,  # 90s decade
            "uncertainty_high": 0.5,
            "bmi_low": 18.5,
            "bmi_high": 30,
            "weight_low": 50,
            "weight_high": 250
        }

        #dynamic thresholds from training data 
        train_data_path = MODEL_DIR/"train_data_for_thresholds.joblib"
        if os.path.exists(train_data_path):
            try:
                train_df = joblib.load(train_data_path)

               
                if "age_decade" in train_df.columns:
                    _thresholds["age_high"] = float(train_df["age_decade"].quantile(0.99))
                elif "age" in train_df.columns:
                    _thresholds["age_high"] = float(train_df["age"].quantile(0.99))

                if "bmi" in train_df.columns:
                    _thresholds["bmi_low"] = float(train_df["bmi"].quantile(0.01))
                    _thresholds["bmi_high"] = float(train_df["bmi"].quantile(0.99))
                if "target" in train_df.columns:
                    _thresholds["dose_high"] = float(train_df["target"].quantile(0.99))
                if "weight_kg" in train_df.columns:
                    _thresholds["weight_low"] = float(train_df["weight_kg"].quantile(0.01))
                    _thresholds["weight_high"] = float(train_df["weight_kg"].quantile(0.99))

            except Exception as e:
                print(f"Warning: Could not compute thresholds: {e}. Using defaults.")

    return _model, _feature_cols, _thresholds

def reload_model():
   
    load_artifacts(force_reload=True)
    return {"status": "reloaded", "model_mtime": _model_mtime}

def model_predict(patient_dict: dict):
    model, feature_cols, thresholds = load_artifacts()

    raw = {
        'age': patient_dict['age'], 
        'gender': patient_dict['gender'],
        'race': patient_dict['race'],
        'ethnicity': 'unknown',
        'height_cm': patient_dict['height_cm'],
        'weight_kg': patient_dict['weight_kg'],
        'cyp2c9_genotypes': patient_dict.get('cyp2c9'),
        'vkorc1_1639': patient_dict.get('vkorc1'),
        'diabetes': patient_dict.get('diabetes', 0),
        'congestive_heart_failure_and_or_cardiomyopathy': 0,
        'valve_replacement': 0,
        'medications': patient_dict.get('medications', ''),
        'aspirin': patient_dict.get('aspirin', 0),
        'acetaminophen_or_paracetamol_tylenol': 0,
        'simvastatin_zocor': 0,
        'amiodarone_cordarone': patient_dict.get('amiodarone', 0),
        'carbamazepine_tegretol': 0,
        'phenytoin_dilantin': 0,
        'rifampin_or_rifampicin': patient_dict.get('rifampin', 0),
        'sulfonamide_antibiotics': 0,
        'macrolide_antibiotics': 0,
        'anti_fungal_azoles': 0,
        'current_smoker': 0,
        'comorbidities': patient_dict.get('comorbidities', ''),
        'pharmgkb_subject_id': None,
        'target': None
    }

  
    df = pd.DataFrame([raw])

    df = create_features(df)

    for col in feature_cols:
        if col not in df.columns:
            df[col] = 0
    X_row_df = df[feature_cols]

    prediction = float(model.predict(X_row_df)[0])
    return prediction, thresholds, X_row_df




def save_model(model_obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(model_obj, path)
