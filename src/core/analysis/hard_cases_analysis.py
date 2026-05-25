import pandas as pd
import numpy as np
from pathlib import Path
from src.utils.config import RESULTS_VERSION



def analyse_hard_cases(X_test, y_test, pred, genotype_col="vkorc1",save=False):

    df = X_test.copy()

    df["y_true"] = y_test
    df["y_pred"] = pred
    df["abs_error"] = np.abs(df["y_true"] - df["y_pred"])

    # -------------------------
    # Define top 20% errors
    # -------------------------
    threshold = df["abs_error"].quantile(0.80)

    hard_cases = df[df["abs_error"] >= threshold]
    easy_cases = df[df["abs_error"] < threshold]

    print(f"Hard cases (top 20%): {len(hard_cases)}")
    print(f"Easy cases (bottom 80%): {len(easy_cases)}")
  
    # -------------------------
    # Numeric feature comparison
    # -------------------------
    exclude_cols = ["y_true", "y_pred", "abs_error"]

    comparison = pd.DataFrame({
        "Hard": hard_cases.drop(columns=exclude_cols, errors="ignore").mean(numeric_only=True),
        "Easy": easy_cases.drop(columns=exclude_cols, errors="ignore").mean(numeric_only=True)
    })

    comparison["Diff"] = comparison["Hard"] - comparison["Easy"]

    # Sort by importance
    comparison = (
        comparison
        .reindex(comparison["Diff"].abs().sort_values(ascending=False).index)
        .reset_index()
        .rename(columns={"index": "Feature"})
    )
    if save: 
       
       comparison.to_csv(RESULTS_VERSION/"comparison_of_hard_cases.csv", index=False)
   
    
    print("\nTOP FEATURES DRIVING ERROR (Hard vs Easy):")
    print(comparison.set_index("Feature")["Diff"].head(15))

    # -------------------------
    # Genotype analysis (categorical)
    # -------------------------
    if genotype_col in df.columns:

        hard_dist = hard_cases[genotype_col].value_counts(normalize=True)
        easy_dist = easy_cases[genotype_col].value_counts(normalize=True)

        genotype_comparison = pd.DataFrame({
            "Hard": hard_dist,
            "Easy": easy_dist
        }).fillna(0)

        genotype_comparison["Diff"] = genotype_comparison["Hard"] - genotype_comparison["Easy"]

        if save: 
        
         Path("results").mkdir(parents=True, exist_ok=True)
         genotype_comparison.reset_index().to_csv(RESULTS_VERSION/f"genotype_comparison_{genotype_col}.csv",
         index=False)

        print(f"\nGENOTYPE DISTRIBUTION: {genotype_col}")
        print(genotype_comparison.sort_values("Diff", ascending=False))

    else:
        genotype_comparison = None
        print(f"\nColumn '{genotype_col}' not found — skipping genotype analysis.")

    return hard_cases, easy_cases, comparison, genotype_comparison










