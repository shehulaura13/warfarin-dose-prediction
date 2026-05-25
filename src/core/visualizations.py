import matplotlib.pyplot as plt
from src.utils.config import FIGURES_VERSION

def plot_model_performance(results_df):

   results_df = results_df.sort_values("MAE")

   plt.figure()
   plt.bar(results_df["model"], results_df["MAE"])
   plt.xlabel("Model")
   plt.ylabel("MAE")
   plt.title("Model Comparison (MAE)")

   plt.tight_layout()
   plt.savefig(FIGURES_VERSION/"mae_comparison.png", dpi=300)
   plt.close()
   
def plot_within20(results_df):

   plt.figure()
   plt.bar(results_df["model"], results_df["Within20"])
   plt.xlabel("Model")
   plt.ylabel("Within 20% Accuracy")
   plt.title("Clinical Accuracy (Within 20%)")

   plt.tight_layout()
   plt.savefig(FIGURES_VERSION/"within20.png", dpi=300)
   plt.close()




