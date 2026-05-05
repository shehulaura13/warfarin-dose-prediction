from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer


def build_preprocessor(X):
   
    numeric_features=X.select_dtypes(include=['int64','float64']).columns.tolist()
    genetic_features = ["vkorc1"]
    categorical_features = [col for col in X.select_dtypes(include=['object']).columns.tolist()
                        if col not in genetic_features]
    X[categorical_features]= X[categorical_features].astype(str)

    genetic_pipeline = Pipeline([
    ('encoder', OneHotEncoder(handle_unknown='ignore'))
])


    numerical_pipeline=Pipeline([
       ( 'imputer',SimpleImputer(strategy='median')),
        ('scaler',StandardScaler())]
)

    categorical_pipeline=Pipeline([
       ('imputer',SimpleImputer(strategy='most_frequent')),
       ('encoder',OneHotEncoder(handle_unknown='ignore'))

    ])
    
    preprocess= ColumnTransformer(
        [
            ("num",numerical_pipeline,numeric_features),
            ("cat",categorical_pipeline,categorical_features),
            ("gen", genetic_pipeline, genetic_features)
        ]
    )
    return preprocess





  