import logging
import joblib

from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    HTTPException,
    Request
)

from fastapi.responses import JSONResponse

from fastapi.middleware.cors import CORSMiddleware

from src.api.schemas import (
    PatientRequest,
    DoseResponse,
    HealthResponse
)

from src.api.api_utils import (
    load_artifacts,
    model_predict,
    normalize_patient
)

from src.api.validation import (
    build_api_response,
    check_cpic_hard_gate
)

from src.utils.config import (
    CONFORMAL_Q90_PATH,
    MODEL_VERSION,
    UNCERTAINTY_MODEL_PATH
)



logging.basicConfig(filename="app.log",level=logging.INFO)

logger = logging.getLogger(__name__)



@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info(
        f"Loading Warfarin SaMD {MODEL_VERSION}"
    )

    try:

        model, feature_cols, thresholds = (
            load_artifacts()
        )

        app.state.model = model

        app.state.feature_cols = feature_cols

        app.state.thresholds = thresholds

        app.state.uncertainty_model = joblib.load(UNCERTAINTY_MODEL_PATH)

        logger.info(
            f"Loaded model + "
            f"{len(feature_cols)} features"
        )

        app.state.q90 = joblib.load(
            CONFORMAL_Q90_PATH
        )

        logger.info(
            f"Loaded conformal q90="
            f"{app.state.q90:.3f}"
        )

    except FileNotFoundError as e:

        logger.exception(
            "Critical artifact missing during startup"
        )

        raise RuntimeError(
            f"Startup failed: {e}"
        )

    except Exception:

        logger.exception(
            "Unexpected startup failure"
        )

        raise RuntimeError(
            "API startup failed"
        )

    yield

    logger.info("Shutting down Warfarin API")



app = FastAPI(
    title="Warfarin Dose Prediction SaMD",
    version=MODEL_VERSION,
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)



@app.get(
    "/health",
    response_model=HealthResponse
)
def health():

    return HealthResponse(
        status="healthy",

        version=MODEL_VERSION,

        model_loaded=(
            app.state.model is not None
        ),

        conformal_loaded=(
            app.state.q90 is not None
        )
    )



@app.post(
    "/predict",
    response_model=DoseResponse
)
def predict(
    patient: PatientRequest
):

    try:

        patient_dict = normalize_patient(
            patient.model_dump()
        )

        logger.info(
            f"Prediction request | "
            f"age={patient_dict.get('age')} | "
            f"cyp={patient_dict.get('cyp2c9_genotypes')}"
        )

    

        override = check_cpic_hard_gate(
            patient_dict
        )

        if override:

            logger.warning(
                f"CPIC override triggered | "
                f"{override.get('reason')}"
            )

            return DoseResponse(**override)

     
        prediction, X_row_df = model_predict(
            patient_dict=patient_dict,
            model=app.state.model,
            feature_cols=app.state.feature_cols
        )

      

        response_dict = build_api_response(
            pipeline=app.state.model,

            uncertainty_model = app.state.uncertainty_model,

            X_row_df=X_row_df,

            thresholds=app.state.thresholds,

            patient_dict=patient_dict,

            q90=app.state.q90
        )

        logger.info(
            f"Prediction complete | "
            f"dose={response_dict.get('dose_mg_per_week')} | "
            f"refused={response_dict.get('refused')}"
        )

        return DoseResponse(**response_dict)



    except ValueError as e:

        logger.warning(
            f"Validation error: {e}"
        )

        raise HTTPException(
            status_code=422,
            detail=str(e)
        )

  

    except Exception:

        logger.exception(
            "Unexpected inference failure"
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )



@app.post("/reload")
def reload_artifacts():

    try:

        logger.warning(
            "Manual artifact reload triggered"
        )

        model, feature_cols, thresholds = (
            load_artifacts(force_reload=True)
        )

        app.state.model = model

        app.state.feature_cols = feature_cols

        app.state.thresholds = thresholds

        app.state.uncertainty_model = joblib.load(UNCERTAINTY_MODEL_PATH)

        app.state.q90 = joblib.load(
            CONFORMAL_Q90_PATH
        )

        logger.info(
            "Artifact reload successful"
        )

        return {
            "status": "reloaded",
            "model_version": MODEL_VERSION,
            "features": len(feature_cols)
        }

    except Exception:

        logger.exception(
            "Reload failed"
        )

        raise HTTPException(
            status_code=500,
            detail="Reload failed"
        )



@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):

    logger.exception(
        f"Unhandled exception: {exc}"
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail":
                "Internal server error"
        }
    )




