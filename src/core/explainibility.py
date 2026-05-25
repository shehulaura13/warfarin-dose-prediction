import shap
import matplotlib.pyplot as plt
import pandas as pd
from src.utils.config import FIGURES_VERSION


def shap_analysis(model,X_test):
    X_sample=X_test.sample(50)
    preprocessor = model.named_steps["preprocessor"]
    xgb_model = model.named_steps["model"]

    
    X_test_transformed = preprocessor.transform(X_sample)
   
    feature_names = preprocessor.get_feature_names_out()
 

    explainer = shap.TreeExplainer(xgb_model,feature_perturbation="tree_path_dependent")

    
    shap_values = explainer.shap_values(X_test_transformed)
   
    X_plot=pd.DataFrame(X_test_transformed.toarray() if hasattr(X_test_transformed,"toarray") else X_test_transformed,columns=feature_names)
 
    shap.summary_plot(
        shap_values,
        X_plot,
        max_display=20,
        show=False
    )
    plt.tight_layout()
    plt.savefig(FIGURES_VERSION/"shap_summary.png",dpi=300)
    plt.close()
    