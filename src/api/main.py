from fastapi import FastAPI, HTTPException
from.schemas import PatientRequest, DoseResponse
from.api_utils import model_predict, load_artifacts
from.validation import build_api_response
import logging


logger = logging.getLogger(__name__)



app = FastAPI(title="Warfarin Dose Prediction API")
def normalize_patient(patient):
    
    return {
        **patient,
        "cyp2c9": patient.get("cyp2c9","") or patient.get("cyp2c9_genotypes",""),
        "vkorc1": patient.get("vkorc1","") or patient.get("vkorc1_1639",""),
       
        "cyp2c9_genotypes": patient.get("cyp2c9_genotypes","") or patient.get("cyp2c9",""),
        "vkorc1_1639": patient.get("vkorc1_1639","") or patient.get("vkorc1",""),
    }

_model, _feature_cols, _thresholds = load_artifacts()

@app.post("/predict", response_model=DoseResponse)
def predict(patient: PatientRequest):
    try:
     
        patient_dict = normalize_patient(patient.model_dump())
        logger.info(f"Flag inputs: age={patient_dict['age']}, cyp={patient_dict.get('cyp2c9_genotypes')}, amio={patient_dict.get('amiodarone')}")

        prediction, thresholds, X_row_df = model_predict(patient_dict)

       
        response_dict = build_api_response(
            pipeline= _model, 
            X_row_df=X_row_df,
            thresholds=thresholds,
            patient_dict=patient_dict
           
        )

        return DoseResponse(**response_dict)

    except ValueError as e:
      
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")

@app.post("/reload")
def reload():
    from .api_utils import reload_model
    return reload_model()


