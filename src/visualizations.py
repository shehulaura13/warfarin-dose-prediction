import matplotlib.pyplot as plt

def plot_model_performance(results_df):

   results_df = results_df.sort_values("MAE")

   plt.figure()
   plt.bar(results_df["model"], results_df["MAE"])
   plt.xlabel("Model")
   plt.ylabel("MAE")
   plt.title("Model Comparison (MAE)")

   plt.tight_layout()
   plt.savefig("figures/mae_comparison.png", dpi=300)
   plt.close()
   
def plot_within20(results_df):

   plt.figure()
   plt.bar(results_df["model"], results_df["Within20"])
   plt.xlabel("Model")
   plt.ylabel("Within 20% Accuracy")
   plt.title("Clinical Accuracy (Within 20%)")

   plt.tight_layout()
   plt.savefig("figures/within20.png", dpi=300)
   plt.close()




