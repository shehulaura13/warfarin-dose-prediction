import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_DIR = BASE_DIR / "models"
FIGURES_DIR = BASE_DIR / "figures"
RESULTS_DIR = BASE_DIR / "results"
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH= DATA_DIR/"raw_data"/"warfarin.csv"
DATA_PROCESSED = DATA_DIR / "processed_data"

# Model artifacts
MODEL_PATH = MODEL_DIR / "xgb_model.joblib"
FEATURES_PATH = MODEL_DIR / "feature_columns_x_train.joblib"
TRAIN_DATA_PATH = MODEL_DIR / "train_data_for_thresholds.joblib"

# Processed data 
X_TRAIN_PATH = DATA_PROCESSED / "X_train.joblib"
X_TEST_PATH = DATA_PROCESSED / "X_test.joblib"
Y_TRAIN_PATH = DATA_PROCESSED / "y_train.joblib"
Y_TEST_PATH = DATA_PROCESSED / "y_test.joblib"

for p in [MODEL_DIR, FIGURES_DIR, RESULTS_DIR, DATA_DIR]:
    os.makedirs(p, exist_ok=True)



