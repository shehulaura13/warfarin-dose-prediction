import joblib
import json
import numpy as np
from sklearn.model_selection import KFold
from sklearn.base import clone
from datetime import datetime
from pathlib import Path
from src.utils.config import(
    CALIBRATION_SET_PATH,
    CONFORMAL_Q90_PATH,
    METADATA_PATH,
    UNCERTAINTY_MODEL_PATH,X_CAL_PATH,X_TRAIN_PATH,Y_CAL_PATH
)



def generate_oof_residuals(pipeline,X_train,y_train,n_splits=5):


    kf = KFold(n_splits=n_splits,shuffle=True,random_state=42)
    oof_preds = np.zeros(len(X_train))



    for fold, (train_idx, val_idx) in enumerate(kf.split(X_train)):


        print(f"OOF Fold {fold+1}")

        X_tr = X_train.iloc[train_idx]

        y_tr = y_train.iloc[train_idx]

        X_val = X_train.iloc[val_idx]

        fold_model = clone(pipeline)

        fold_model.fit(X_tr, y_tr)

        preds = fold_model.predict(X_val)

        oof_preds[val_idx] = preds

        residuals = np.abs(

        y_train.values - oof_preds)



    return residuals




def train_uncertainty_model(pipeline,X_train,y_train):


    print("Generating OOF residuals...")

    residuals = generate_oof_residuals(pipeline,X_train,y_train)

    print(

    f"Residual mean: "
    f"{residuals.mean():.2f}")


    residual_targets = np.log1p(residuals)
    uncertainty_model = clone(pipeline)

    print("Training uncertainty model...")

    uncertainty_model.fit(X_train, residual_targets)

    joblib.dump(uncertainty_model,UNCERTAINTY_MODEL_PATH)



    print(
    f"Saved uncertainty model:"
    f" {UNCERTAINTY_MODEL_PATH}")


    return uncertainty_model



def predict_uncertainty(uncertainty_model, X_row_df):


    log_uncertainty = (uncertainty_model.predict(X_row_df)[0])

    uncertainty = np.expm1(log_uncertainty)
    uncertainty = max(uncertainty,1.0)


    return float(uncertainty)


def build_and_save_calibration(model,uncertainty_model,X_cal,y_cal,X_train):
    X_cal = joblib.load(X_CAL_PATH)
    y_cal = joblib.load(Y_CAL_PATH)
    X_train = joblib.load(X_TRAIN_PATH)

    cal_preds = model.predict(X_cal)

    cal_uncertainties = np.array([predict_uncertainty(uncertainty_model,X_cal.iloc[[i]])

        for i in range(len(X_cal))])


    calibration_artifact = {"y_true": (y_cal.values


                            if hasattr(y_cal, "values")
                            else y_cal),

                            "y_pred": cal_preds,

                            "uncertainty": cal_uncertainties

        }

    joblib.dump(calibration_artifact,CALIBRATION_SET_PATH)


    scores = (

            np.abs(calibration_artifact["y_true"]-calibration_artifact["y_pred"])/
            np.maximum(calibration_artifact["uncertainty"],1e-6)
)

    scores = np.clip(scores,0,10)

    q90 = np.quantile(scores,0.90)

    joblib.dump(q90,CONFORMAL_Q90_PATH)



    metadata = {


            "version": "v1.2.0",



            "training_date": str(datetime.now()),



            "train_size": int(len(X_train)),



            "calibration_size": int(len(X_cal)),



            "q90": float(q90)



        }



    with open(METADATA_PATH, "w") as f:



            json.dump(metadata,f,indent=4)



    print(f"Saved q90: {q90:.3f}")



    return q90






def get_conformal_interval( y_pred,uncertainty,q90):



    
    uncertainty = max(uncertainty,1.0)



    margin = q90 * uncertainty



    lower = max(0.0,y_pred - margin)



    upper = y_pred + margin



    width = upper - lower



    refused = width > 50



    if refused:


       return None, None, True



    return (

        round(lower, 1),
        round(upper, 1),
        False

)

