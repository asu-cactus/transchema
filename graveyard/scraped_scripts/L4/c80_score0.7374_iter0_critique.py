import pandas as pd
import numpy as np

# Read source files with index_col=0 as instructed
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_80/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_80/training_1.csv", index_col=0)

# Join on Mouse ID (string)
joined = pd.merge(df0, df1, on="Mouse ID", how="inner")

# Define a function to compute SEM safely
def sem(x):
    return x.std(ddof=1) / np.sqrt(len(x)) if len(x) > 1 else 0

# Group by Drug and Timepoint (leftmost non-float unique columns)
grouped = joined.groupby(["Drug", "Timepoint"], as_index=False).agg(
    **{
        "Mean of Tumor Volume (mm3)": ("Tumor Volume (mm3)", "mean"),
        "SEM of Tumor Volume (mm3)": ("Tumor Volume (mm3)", sem),
        "Mouse ID": ("Mouse ID", lambda x: x.nunique()),
        "Metastatic Sites": ("Metastatic Sites", "mean"),
    }
)

# Convert types to match target schema
grouped["Drug"] = grouped["Drug"].astype(str)
grouped["Timepoint"] = grouped["Timepoint"].astype(int)
grouped["Mouse ID"] = grouped["Mouse ID"].astype(int)
grouped["SEM of Tumor Volume (mm3)"] = grouped["SEM of Tumor Volume (mm3)"].round().astype(int)
grouped["Metastatic Sites"] = grouped["Metastatic Sites"].round().astype(int)

# Reorder columns to match target schema exactly
grouped = grouped[["Drug", "Timepoint", "Mean of Tumor Volume (mm3)", "Mouse ID", "SEM of Tumor Volume (mm3)", "Metastatic Sites"]]

# Write output
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_80/target_multisource_mcts.csv", index=False)