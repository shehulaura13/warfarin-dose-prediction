import joblib
import numpy as np
from sklearn.metrics import mean_absolute_error

from src.core.uncertainty import (
    train_uncertainty_model,
    predict_uncertainty,
    get_conformal_interval
)

from src.utils.config import (
    MODEL_PATH,
    X_TEST_PATH,
    Y_TEST_PATH,
    CONFORMAL_Q90_PATH,
    UNCERTAINTY_MODEL_PATH,
    RESULTS_VERSION
)

print("=== Loading artifacts ===")

model = joblib.load(MODEL_PATH)
X_test = joblib.load(X_TEST_PATH)
y_test = joblib.load(Y_TEST_PATH)
q90 = joblib.load(CONFORMAL_Q90_PATH)
uncertainty_model = joblib.load(UNCERTAINTY_MODEL_PATH)

print(f"Test size: {len(X_test)}")
print(f"q90: {q90:.3f}")

# =========================================================
# STEP 1 — Predictions
# =========================================================

print("\n=== Computing predictions + uncertainty on TEST ===")


# Main predictions
y_pred = model.predict(X_test)


test_stds = np.array([

    predict_uncertainty(
        uncertainty_model,
        X_test.iloc[[i]]
    )

    for i in range(len(X_test))

])

print(
    f"test_stds min/max/mean: "
    f"{test_stds.min():.2f} / "
    f"{test_stds.max():.2f} / "
    f"{test_stds.mean():.2f}"
)



# =========================================================
# STEP 2 — Conformal Prediction Intervals
# =========================================================

print("\n=== Computing Conformal Prediction Intervals ===")

results = [
    get_conformal_interval(
        y_pred=p,
        uncertainty=s,
        q90=q90
    )
    for p, s in zip(y_pred, test_stds)
]

lower_pi = np.array([
    r[0] if r[0] is not None else np.nan
    for r in results
])

upper_pi = np.array([
    r[1] if r[1] is not None else np.nan
    for r in results
])

refused = np.array([
    r[2]
    for r in results
])

accepted_mask = ~refused

# =========================================================
# STEP 3 — PI Statistics
# =========================================================

pi_widths = upper_pi - lower_pi

relative_width = pi_widths / np.maximum(y_pred, 1e-6)

accepted = accepted_mask.sum()

# =========================================================
# STEP 4 — Coverage
# =========================================================

covered = (
    (y_test >= lower_pi)
    &
    (y_test <= upper_pi)
)

coverage = (
    np.mean(covered[accepted_mask])
    if np.any(accepted_mask)
    else 0.0
)

# =========================================================
# STEP 5 — Refusal Rate
# =========================================================

refusal_rate = np.mean(refused)

# =========================================================
# STEP 6 — Point Prediction Metrics
# =========================================================

mae = mean_absolute_error(
    y_test,
    y_pred
)

# IWPC ±20% rule
ideal_dose = (
    np.abs(y_pred - y_test)
    <=
    (0.2 * y_test)
)

ideal_dose_rate = np.mean(ideal_dose)

# =========================================================
# STEP 7 — Width Metrics
# =========================================================

median_width = np.nanmedian(pi_widths)

median_width_accepted = (
    np.nanmedian(pi_widths[accepted_mask])
    if np.any(accepted_mask)
    else np.nan
)

median_relative_width = np.nanmedian(relative_width)

# =========================================================
# STEP 8 — Print Results
# =========================================================

print("\n=== CONFORMAL RESULTS ===")

print(f"q90: {q90:.3f}")

print(
    f"Coverage (accepted only): "
    f"{coverage*100:.1f}%"
)

print(
    f"Accepted: "
    f"{accepted}/{len(y_test)}"
)

print(
    f"Refused: "
    f"{refused.sum()}/{len(y_test)} "
    f"= {refusal_rate*100:.1f}%"
)

print(
    f"Median PI Width (all): "
    f"{median_width:.1f} mg/week"
)

print(
    f"Median PI Width (accepted): "
    f"{median_width_accepted:.1f} mg/week"
)

print(
    f"Median Relative PI Width: "
    f"{median_relative_width*100:.1f}%"
)

# =========================================================
# STEP 9 — Point Prediction Metrics
# =========================================================

print("\n=== POINT PREDICTION METRICS ===")

print(f"Test MAE: {mae:.2f} mg/week")

print(
    f"Ideal Dose Rate (±20% IWPC): "
    f"{ideal_dose_rate*100:.1f}%"
)

# =========================================================
# STEP 10 — Stratified Clinical Analysis
# =========================================================

low_dose = y_test <= 21

med_dose = (
    (y_test > 21)
    &
    (y_test < 49)
)

high_dose = y_test >= 49

print("\n=== Stratified by Actual Dose ===")

if np.any(low_dose):

    print(
        f"Low ≤21 mg/wk: "
        f"n={low_dose.sum()}, "
        f"Ideal={np.mean(ideal_dose[low_dose])*100:.1f}%, "
        f"Refused={np.mean(refused[low_dose])*100:.1f}%"
    )

if np.any(med_dose):

    print(
        f"Med 21-49 mg/wk: "
        f"n={med_dose.sum()}, "
        f"Ideal={np.mean(ideal_dose[med_dose])*100:.1f}%, "
        f"Refused={np.mean(refused[med_dose])*100:.1f}%"
    )

if np.any(high_dose):

    print(
        f"High ≥49 mg/wk: "
        f"n={high_dose.sum()}, "
        f"Ideal={np.mean(ideal_dose[high_dose])*100:.1f}%, "
        f"Refused={np.mean(refused[high_dose])*100:.1f}%"
    )

# =========================================================
# STEP 11 — Save Results
# =========================================================

results_dict = {
    "q90": float(q90),

    "coverage": float(coverage),

    "accepted_predictions": int(accepted),

    "refusal_rate": float(refusal_rate),

    "median_pi_width": (
        float(median_width)
        if not np.isnan(median_width)
        else None
    ),

    "median_pi_width_accepted": (
        float(median_width_accepted)
        if not np.isnan(median_width_accepted)
        else None
    ),

    "median_relative_width": (
        float(median_relative_width)
        if not np.isnan(median_relative_width)
        else None
    ),

    "mae": float(mae),

    "ideal_dose_rate": float(ideal_dose_rate),

    "n_test": int(len(y_test)),

    "n_refused": int(refused.sum()),

    "rule": "split_conformal_prediction"
}

joblib.dump(
    results_dict,
    RESULTS_VERSION/"conformal_results_v1.2.joblib"
)

print(
    "\nSaved: RESULTS_VERSION/conformal_results_v1.2.joblib"
)


