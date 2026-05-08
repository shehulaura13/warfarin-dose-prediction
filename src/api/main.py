import logging

from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from .schemas import (
    PatientRequest,
    DoseResponse
)

from .api_utils import (
    load_artifacts,
    model_predict
)

from .validation import (
    build_api_response,
    check_cpic_hard_gate
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Loading model artifacts...")

    model, feature_cols, thresholds = load_artifacts()

    app.state.model = model
    app.state.feature_cols = feature_cols
    app.state.thresholds = thresholds

    logger.info(
        f"Model loaded successfully. "
        f"Features: {len(feature_cols)}"
    )

    yield

    logger.info("Shutting down API")


app = FastAPI(
    title="Warfarin Dose Prediction API",
    lifespan=lifespan
)


def normalize_patient(patient):

    return {
        **patient,

        "cyp2c9":
            patient.get("cyp2c9", "")
            or patient.get("cyp2c9_genotypes", ""),

        "vkorc1":
            patient.get("vkorc1", "")
            or patient.get("vkorc1_1639", ""),

        "cyp2c9_genotypes":
            patient.get("cyp2c9_genotypes", "")
            or patient.get("cyp2c9", ""),

        "vkorc1_1639":
            patient.get("vkorc1_1639", "")
            or patient.get("vkorc1", ""),
    }


@app.post(
    "/predict",
    response_model=DoseResponse
)
def predict(patient: PatientRequest):

    try:

        
        patient_dict = normalize_patient(
            patient.model_dump()
        )

       
        override = check_cpic_hard_gate(patient_dict)

        if override:

            logger.warning(
                f"CPIC override triggered for "
                f"{patient_dict.get('cyp2c9_genotypes')}"
            )

            return DoseResponse(**override)

       

        prediction, X_row_df = model_predict(
            patient_dict=patient_dict,
            model=app.state.model,
            feature_cols=app.state.feature_cols
        )

      

        response_dict = build_api_response(
            pipeline=app.state.model,
            X_row_df=X_row_df,
            thresholds=app.state.thresholds,
            patient_dict=patient_dict
        )

        return DoseResponse(**response_dict)

    except ValueError as e:

        raise HTTPException(
            status_code=422,
            detail=str(e)
        )

    except Exception as e:

        logger.exception("Inference failed")

        raise HTTPException(
            status_code=500,
            detail=f"Inference failed: {str(e)}"
        )




@app.post("/reload")
def reload():

    try:

        logger.info("Reloading model artifacts...")

        model, feature_cols, thresholds = load_artifacts()

        app.state.model = model
        app.state.feature_cols = feature_cols
        app.state.thresholds = thresholds

        logger.info("Reload successful")

        return {
            "status": "reloaded",
            "features": len(feature_cols)
        }

    except Exception as e:

        logger.exception("Reload failed")

        raise HTTPException(
            status_code=500,
            detail=f"Reload failed: {str(e)}"
        )




