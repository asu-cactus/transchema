import pandas as pd
import numpy as np

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_1.csv", index_col=0)

# Join on Mouse ID
merged = pd.merge(df0, df1, on="Mouse ID", how="inner")

# Group by Drug and Timepoint
grouped = merged.groupby(["Drug", "Timepoint"], as_index=False).agg(
    **{
        "Mean of Metastatic Sites": ("Metastatic Sites", "mean"),
        "SEM of Metastatic Sites": lambda x: x.std(ddof=1) / np.sqrt(len(x)) if len(x) > 1 else 0,
        "Mouse ID": ("Mouse ID", pd.Series.nunique),
        "Tumor Volume (mm3)": ("Tumor Volume (mm3)", "mean"),
    }
)

# Round and convert types to match target schema
grouped["Timepoint"] = grouped["Timepoint"].astype(int)
grouped["Mean of Metastatic Sites"] = grouped["Mean of Metastatic Sites"].astype(float)
grouped["SEM of Metastatic Sites"] = grouped["SEM of Metastatic Sites"].round().astype("Int64")
grouped["Mouse ID"] = grouped["Mouse ID"].astype("Int64")
grouped["Tumor Volume (mm3)"] = grouped["Tumor Volume (mm3)"].round().astype("Int64")

# Reorder columns to match target schema
result = grouped[["Drug", "Timepoint", "Mean of Metastatic Sites", "Mouse ID", "Tumor Volume (mm3)", "SEM of Metastatic Sites"]]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_81/target_multisource_mcts.csv", index=False)