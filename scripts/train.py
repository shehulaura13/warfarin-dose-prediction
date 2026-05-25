from pathlib import Path
import pandas as pd
import mlflow
import joblib
import mlflow.sklearn
from src.core.data_loading import data_loading
from src.core.data_spliting import split_data
from src.core.data_cleaning import clean_data
from src.core.features import create_features
from src.core.modeling import predict_iwpc, train_linear, train_rf_grid,train_xgboost_model
from src.core.explainibility import shap_analysis
from src.core.evaluations import full_clinical_evaluation
from src.core.visualizations import plot_model_performance, plot_within20
from src.utils.utils import save_model
from src.core.analysis.bleeding_risk_analysis import run_clinical_analysis
from src.core.analysis.hard_cases_analysis import analyse_hard_cases
import mlflow
import mlflow.sklearn
from src.utils.config import MODEL_PATH,DATA_VERSION,RAW_DATA_PATH,X_TRAIN_PATH,X_TEST_PATH,X_CAL_PATH,Y_CAL_PATH,Y_TEST_PATH,Y_TRAIN_PATH,THRESHOLDS_PATH,FEATURES_PATH,RESULTS_VERSION,FIGURES_VERSION
from src.core.uncertainty import build_and_save_calibration,train_uncertainty_model



pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

def run_pipeline():
    mlflow.set_experiment("Warfarin_dosing")
  
    
    df = data_loading(RAW_DATA_PATH)
    df = clean_data(df)
    df.to_csv(DATA_VERSION/"schemas_columns_input.csv")
    df = create_features(df)

    id_cols=[c for c in df.columns if 'subject' in c.lower()]
    id_col=id_cols[0] if id_cols else None

    train_df,calibration_df,test_df = split_data(df, id_col)
    train_df=train_df.reset_index(drop=True)
    calibration_df=calibration_df.reset_index(drop=True)
    test_df=test_df.reset_index(drop=True)
    Path("models").mkdir(exist_ok=True)
    joblib.dump(train_df,THRESHOLDS_PATH)

    X_train = train_df.drop(['target',id_col], axis=1)
    y_train = train_df['target']

    X_calibration = calibration_df.drop(['target', id_col],axis=1)
    y_calibration = calibration_df['target']

    X_test = test_df.drop(['target',id_col],axis=1)
    y_test = test_df['target']

    joblib.dump(X_train, X_TRAIN_PATH)  
    joblib.dump(X_test, X_TEST_PATH) 
    joblib.dump(X_calibration,X_CAL_PATH)
    joblib.dump(y_calibration,Y_CAL_PATH)  
    joblib.dump(y_train, Y_TRAIN_PATH)
    joblib.dump(y_test, Y_TEST_PATH)

    with mlflow.start_run():
   
     results = []

    # -------------------------
    # IWPC BASELINE
    # -------------------------
    base_pred = predict_iwpc(X_test)
    results.append({'model': 'IWPC',
                    **full_clinical_evaluation("IWPC",X_test,y_test,base_pred)
                    })
    # -------------------------
    # LINEAR
    # -------------------------
    lin = train_linear(X_train, y_train)
    lin_pred = lin.predict(X_test)
    results.append({'model': 'Linear',
                    **full_clinical_evaluation("Linear",X_test,y_test,lin_pred)
                   })
    # -------------------------
    # RANDOM FOREST 
    # -------------------------
    rf, params = train_rf_grid(X_train, y_train)
    rf_pred = rf.predict(X_test)
    results.append({
        'model': 'RF',
        'params': str(params),
        **full_clinical_evaluation("RF",X_test,y_test,rf_pred)
       })
 
    # -------------------------
    # XGBOOST
    # -------------------------
    xgb,params = train_xgboost_model(X_train, y_train)
    joblib.dump(X_train.columns.tolist(),FEATURES_PATH)
    
    save_model(xgb,MODEL_PATH)
    uncertainty_model = train_uncertainty_model(xgb,X_train,y_train)
    build_and_save_calibration(xgb,uncertainty_model,X_calibration,y_calibration,X_train)
    
     
    
    mlflow.sklearn.log_model(xgb, "model")
    mlflow.log_params(params, "XGBOOST best params")
    
    xgb_pred = xgb.predict(X_test)
   
    results.append({
        'model': 'XGBOOST',
        'params': str(params),
       **full_clinical_evaluation("XGBOOST",X_test,y_test,xgb_pred)
       
    })
    results_df = pd.DataFrame(results)
    results_df=results_df.sort_values("MAE")
    results_df.to_csv(RESULTS_VERSION/"models_comparison.csv")
    print(results_df,flush=True)

    mlflow.log_metrics({
       "mae":results_df["MAE"].min(),
       "within20":results_df["Within20"].max(),
       "Hard_cases_MAE":results_df["Hard_cases_MAE"].min()


    })
    #XGBOOST ANALYSIS
    shap= shap_analysis(xgb,X_test)
    hard_cases,easy_cases,comparison,genotype_comparison=analyse_hard_cases(X_test,y_test,xgb_pred,save=True)
    run_clinical_analysis(X_test,y_test,xgb_pred)

    
    mlflow.log_artifact(RESULTS_VERSION/"comparison_of_hard_cases.csv")
    mlflow.log_artifact(RESULTS_VERSION/"genotype_comparison_vkorc1.csv")
    mlflow.log_artifact(RESULTS_VERSION/"bleeding_risk_analysis.csv")
    mlflow.log_artifact(RESULTS_VERSION/"models_comparison.csv")
    plot_model_performance(results_df)
    plot_within20(results_df)
    mlflow.log_artifact(FIGURES_VERSION/"mae_comparison.png")
    mlflow.log_artifact(FIGURES_VERSION/"within20.png")
    mlflow.log_artifact(FIGURES_VERSION/"shap_summary.png")

    return results_df

   
if __name__ == "__main__":
    run_pipeline()

