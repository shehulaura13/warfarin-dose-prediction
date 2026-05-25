import os
from pathlib import Path

MODEL_VERSION = "v1.2.0"

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_DIR = BASE_DIR / "models"
VERSION_DIR = MODEL_DIR / MODEL_VERSION
FIGURES_DIR = BASE_DIR / "figures"
FIGURES_VERSION = FIGURES_DIR / MODEL_VERSION
RESULTS_DIR = BASE_DIR / "results"
RESULTS_VERSION = RESULTS_DIR / MODEL_VERSION
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH= DATA_DIR/"raw_data"/"warfarin.csv"
DATA_PROCESSED = DATA_DIR / "processed_data"
DATA_VERSION = DATA_PROCESSED / MODEL_VERSION

# Model artifacts
MODEL_PATH = VERSION_DIR / "xgb_model.joblib"
UNCERTAINTY_MODEL_PATH = VERSION_DIR / "uncertainty_model.joblib"
FEATURES_PATH = VERSION_DIR / "feature_columns_x_train.joblib"
THRESHOLDS_PATH = VERSION_DIR/ "train_data_for_thresholds.joblib"
CALIBRATION_SET_PATH = VERSION_DIR / "calibration_set.joblib"
CONFORMAL_Q90_PATH = VERSION_DIR / "conformal_q.joblib"
METADATA_PATH = VERSION_DIR / "metadata.json"

# Processed data 
X_TRAIN_PATH = DATA_VERSION / "X_train.joblib"
X_TEST_PATH = DATA_VERSION / "X_test.joblib"
X_CAL_PATH = DATA_VERSION / "X_calibration.joblib"
Y_CAL_PATH = DATA_VERSION / "y_calibration.joblib"
Y_TRAIN_PATH = DATA_VERSION / "y_train.joblib"
Y_TEST_PATH = DATA_VERSION / "y_test.joblib"

for p in [MODEL_DIR, FIGURES_DIR, RESULTS_DIR, DATA_DIR,VERSION_DIR,DATA_VERSION,RESULTS_VERSION,FIGURES_VERSION]:
    os.makedirs(p, exist_ok=True)



