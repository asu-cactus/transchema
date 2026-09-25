import pandas as pd
import numpy as np

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_80/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_80/training_1.csv", index_col=0)

# Join on Mouse ID
df_merged = pd.merge(df0, df1, on="Mouse ID", how='inner')

# Rename columns to match target schema for clarity
df_merged = df_merged.rename(columns={"Tumor Volume (mm3)": "Tumor Volume (mm3)"})

# Group by Drug and Timepoint
group_cols = ["Drug", "Timepoint"]

# Define aggregation functions
def sem(x):
    return x.std(ddof=1) / np.sqrt(len(x)) if len(x) > 1 else 0.0

agg_df = df_merged.groupby(group_cols).agg(
    **{
        "Mean of Tumor Volume (mm3)": ("Tumor Volume (mm3)", "mean"),
        "Mouse ID": ("Mouse ID", pd.Series.nunique),
        "SEM of Tumor Volume (mm3)": ("Tumor Volume (mm3)", sem),
        "Metastatic Sites": ("Metastatic Sites", "mean"),
    }
).reset_index()

# Cast columns to target types
agg_df["Timepoint"] = agg_df["Timepoint"].astype(int)
agg_df["Mean of Tumor Volume (mm3)"] = agg_df["Mean of Tumor Volume (mm3)"].astype(float)
agg_df["Mouse ID"] = agg_df["Mouse ID"].astype(int)
agg_df["SEM of Tumor Volume (mm3)"] = agg_df["SEM of Tumor Volume (mm3)"].astype(float)
agg_df["Metastatic Sites"] = agg_df["Metastatic Sites"].round().astype(int)  # rounding mean to int

# Reorder columns to match target schema
agg_df = agg_df[["Drug", "Timepoint", "Mean of Tumor Volume (mm3)", "Mouse ID", "SEM of Tumor Volume (mm3)", "Metastatic Sites"]]

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_80/target_multisource_mcts.csv", index=False)