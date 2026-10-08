import pandas as pd
import numpy as np

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_80/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_80/training_1.csv", index_col=0)

# Convert Mouse ID in source0 to string to match source1
source0["Mouse ID"] = source0["Mouse ID"].astype(str)
source1["Mouse ID"] = source1["Mouse ID"].astype(str)

# Merge on Mouse ID
merged = pd.merge(source0, source1, on="Mouse ID", how="inner")

# Extract numeric part of Mouse ID and convert to int
merged["Mouse ID"] = merged["Mouse ID"].str.extract(r'(\d+)').astype(int)

# Group by Drug, Timepoint, Mouse ID
grouped = merged.groupby(["Drug", "Timepoint", "Mouse ID"], as_index=False).agg({
    "Tumor Volume (mm3)": ["mean", "sem"],
    "Metastatic Sites": "mean"
})

# Flatten MultiIndex columns
grouped.columns = ["Drug", "Timepoint", "Mouse ID", "Mean of Tumor Volume (mm3)", "SEM of Tumor Volume (mm3)", "Metastatic Sites"]

# Convert Metastatic Sites to int (rounding mean)
grouped["Metastatic Sites"] = grouped["Metastatic Sites"].round().astype(int)

# Convert columns to target types
grouped["Drug"] = grouped["Drug"].astype(str)
grouped["Timepoint"] = grouped["Timepoint"].astype(int)
grouped["Mean of Tumor Volume (mm3)"] = grouped["Mean of Tumor Volume (mm3)"].astype(float)
grouped["SEM of Tumor Volume (mm3)"] = grouped["SEM of Tumor Volume (mm3)"].astype(float)
grouped["Mouse ID"] = grouped["Mouse ID"].astype(int)

# Reorder columns to match target schema
grouped = grouped[["Drug", "Timepoint", "Mean of Tumor Volume (mm3)", "Mouse ID", "SEM of Tumor Volume (mm3)", "Metastatic Sites"]]

# Write output
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_80/target_multisource_mcts.csv", index=False)