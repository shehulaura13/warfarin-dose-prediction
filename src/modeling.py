import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV,RandomizedSearchCV
from sklearn.pipeline import Pipeline
from src.preprocess import build_preprocessor
from xgboost import XGBRegressor


# -------------------------
# IWPC BASELINE
# -------------------------
def predict_iwpc(df):
    age = df['age_decade']
    height = df['height_cm']
    weight = df['weight_kg']
    amiodarone = df['amiodarone']
   
    cyp = df['cyp2c9'].map({
        2.0: 0,
        1.5: -0.5211,
        1.0: -0.9351,
        1.0: -1.0422,
        0.5: -1.4562,
        0.0: -1.8702})

    vkorc1 = df['vkorc1'].map({
        'GG': 0,
        'AG': -0.8677,
        'AA': -1.6974
    })

    dose = (
        4.0376
        - 0.2546 * age
        + 0.0118 * height
        + 0.0134 * weight
        - 0.6752 * amiodarone
        + cyp
        + vkorc1
    )

    return np.square(dose)

# -------------------------
# LINEAR
# -------------------------
def train_linear(X, y):
    preprocessor = build_preprocessor(X)

    pipe = Pipeline([
        ('prep', preprocessor),
        ('model', LinearRegression())
    ])

    pipe.fit(X, y)
    return pipe

# -------------------------
# RANDOM FOREST (GRID SEARCH)
# -------------------------
def train_rf_grid(X, y):
    preprocessor = build_preprocessor(X)

    pipe = Pipeline([
        ('prep', preprocessor),
        ('model', RandomForestRegressor(random_state=42))
    ])

    param_grid = {
        'model__n_estimators': [200, 300],
        'model__max_depth': [5, 10],
        'model__min_samples_split': [2, 5]
    }

    grid = GridSearchCV(
        pipe,
        param_grid,
        cv=3,
        scoring='neg_mean_absolute_error',
        n_jobs=-1
       )

    grid.fit(X, y)

    return grid.best_estimator_, grid.best_params_

# -------------------------
# XGBOOST (RANDOMIZED SEARCH)
# -------------------------

def train_xgboost_model(X,y,sample_weight=None):
     
     preprocessor = build_preprocessor(X)
     model = XGBRegressor(
         random_state=42,
         n_jobs=-1,
         tree_method="hist"
         
        )

     pipe = Pipeline([
        ("preprocessor", preprocessor),
        ("model", model)
    ])
     
     
     param_grid = {
        "model__n_estimators" : [100,200,300,500,800],
        "model__max_depth": [4, 6,8],
        "model__learning_rate": [0.03,0.05, 0.1],
        "model__subsample" : [0.7,0.8,1],
        "model__colsample_bytree" : [0.7,0.8,1],
        "model__reg_alpha" : [0,0.1,1],
         "model__reg_lambda" : [1,3,5]
       }
     grid = RandomizedSearchCV(
        pipe,
        param_distributions=param_grid,
        n_iter=30,
        scoring="neg_mean_absolute_error",
        cv=5,
        n_jobs=1,
        refit=True,
        verbose=1
    )
     
     fit_params = {}
     if sample_weight is not None:
        fit_params["model__sample_weight"] = sample_weight  
        print(f"Using sample_weight. Upweighted: {(sample_weight > 1).sum()} cases")
     
     grid.fit(X, y,**fit_params)
     print("XGBOOST BEST PARAMS:")
     print(grid.best_params_)
     return grid.best_estimator_,grid.best_params_






