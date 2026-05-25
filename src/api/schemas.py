from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Literal, List
from enum import Enum

class Vkorc1Enum(str, Enum):
    AA = "AA"
    AG = "AG"
    GG = "GG"

class PatientRequest(BaseModel):
    gender: Literal["male", "female"]
    race:  Optional[Literal[
    "white",
    "asian",
    "black_or_african_american",
    "unknown"
]] = None
    age: str = Field(..., description="Age bucket: '10-19', '20-29',... '80-89', '90+'")

    weight_kg: float = Field(..., gt=20, lt=200)
    height_cm: float = Field(..., gt=100, lt=250)

    vkorc1: Optional[Vkorc1Enum] = None
    cyp2c9: Optional[Literal["*1/*1", "*1/*2", "*1/*3", "*2/*2", "*2/*3", "*3/*3"]] = None

    amiodarone: int = Field(0, ge=0, le=1)
    aspirin: int = Field(0, ge=0, le=1)
    rifampin: int = Field(0, ge=0, le=1)

    diabetes: int = Field(0, ge=0, le=1)
    hypertension: int = Field(0, ge=0, le=1)

    comorbidities: str | None = Field(
    default=None,
    description="Semicolon-separated list:'heart_failure';'heart_valve_replacement';'liver_disease';'renal_failure';'cancer'",
    examples=["'heart_failure';'heart_valve_replacement';'liver_disease';'renal_failure';'cancer'"]
)
    medications: str | None = Field(
    default=None,
    description="Semicolon-separated list:'simvastatin';'azole';'fluconazole';'metronidazole';'ibuprofen';'carbamazepine';'phenytoin'",
    examples=["'simvastatin';'azole';'fluconazole';'metronidazole';'ibuprofen';'carbamazepine';'phenytoin'"]
)
    bmi: Optional[float] = None
  

    @field_validator('vkorc1', mode='before')
    @classmethod
    def normalize_vkorc1(cls, v):
        if v is None or v == "":
            return None
        v = str(v).upper().replace('/', '').strip()
        if v in {'GG', 'AG', 'AA'}:
            return v
        raise ValueError(f"VKORC1 must be AA/AG/GG or null, got {v}")
    
    @field_validator('cyp2c9', mode='before')
    @classmethod
    def normalize_cyp2c9(cls, c):
        if c is None:
            return None
        return str(c).replace(' ', '').strip() # "*3 / *3" -> "*3/*3"


    @model_validator(mode='after')
    def compute_and_check_bmi(self):
        
        w, h = self.weight_kg, self.height_cm
        bmi = w / (h/100)**2
        self.bmi = round(bmi, 1)
        if self.bmi > 60 or self.bmi <12:
            raise ValueError(f"BMI{self.bmi} physiologically impossible")
        return self


class PredictionInterval(BaseModel):
    lower: float
    upper : float
    coverage : float = 0.90

class HealthResponse(BaseModel):

    status: str

    version: str

    model_loaded: bool

    conformal_loaded: bool    
       
class DoseResponse(BaseModel):
    dose_mg_per_week: float
    raw_model_dose: float
    uncertainty_std: float
    relative_uncertainty: float
    prediction_interval : Optional[PredictionInterval] = None
    refused : bool = False
    confidence: Literal["low", "medium", "high"]
    confidence_score: float = Field(..., ge=0, le=1)
    method: Optional[str] = None
    reason: Optional[str] = None
    flags: List[str]
    actions: List[str]
    clinical_summary: Optional[str] = None
    shap_explanations: Optional[dict] = None
