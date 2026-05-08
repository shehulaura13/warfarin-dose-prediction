import pytest
from fastapi.testclient import TestClient
from src.api.main import app

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

def base_payload():
    return {
        "age": "60-69", "gender": "male", "race": "white",
        "weight_kg": 70, "height_cm": 175,
        "vkorc1": "AG", "cyp2c9": "*1/*1"
    }


def test_predict_happy_path(client):
    r = client.post("/predict", json=base_payload())
    assert r.status_code == 200
    data = r.json()
    assert 0 < data["dose_mg_per_week"] <= 70
    assert data["confidence"] in ["high", "medium", "low"]


def test_cpic_override_hard_gate(client):
    payload = base_payload()
    payload.update({"cyp2c9": "*3/*3"})
    r = client.post("/predict", json=payload)
    assert r.status_code == 200
    data= r.json()
    assert "cpic_hard_gate" in data["flags"]
    assert data["dose_mg_per_week"] == 20
    assert data["method"] == "CPIC_override_hard_gate"



@pytest.mark.parametrize("weight,height,expected_error", [
    (5, 170, "greater than 20"),     
    (300, 170, "less than 200"), 
    (70, 50, "greater than 100"),                
    (70, 250, "less than 250"),                
])
def test_impossible_patients_422(client,weight, height, expected_error):
    payload = base_payload()
    payload.update({"weight_kg": weight, "height_cm": height})
    r = client.post("/predict", json=payload)
    assert r.status_code == 422
    assert expected_error in str(r.json())


def test_missing_vkorc1_triggers_flag(client):
    payload = base_payload()
    del payload["vkorc1"] 
    r = client.post("/predict", json=payload)
    assert r.status_code == 200
    assert "missing_genetics" in r.json()["flags"]
    assert r.json()["confidence"] == "low"

def test_extreme_bmi_triggers_ood(client):
    payload = base_payload()
    payload.update({"weight_kg": 150, "height_cm": 160}) 
    r = client.post("/predict", json=payload)
    assert r.status_code == 200
    assert "extreme_BMI" in r.json()["flags"]



