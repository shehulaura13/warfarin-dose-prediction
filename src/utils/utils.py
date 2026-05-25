import joblib
import os



def save_model(model_obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(model_obj, path)
