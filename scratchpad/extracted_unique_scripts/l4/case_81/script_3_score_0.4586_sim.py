import pandas as pd
import numpy as np

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_1.csv", index_col=0)

merged = pd.merge(source0, source1, on="Mouse ID")

grouped = merged.groupby(["Drug", "Timepoint", "Mouse ID"], as_index=False).agg({
    "Metastatic Sites": ["mean", "sem"],
    "Tumor Volume (mm3)": "mean"
})

grouped.columns = ["Drug", "Timepoint", "Mouse ID", "Mean of Metastatic Sites", "SEM of Metastatic Sites", "Tumor Volume (mm3)"]

grouped["Timepoint"] = grouped["Timepoint"].astype(int)
grouped["Mean of Metastatic Sites"] = grouped["Mean of Metastatic Sites"].astype(float)
grouped["Mouse ID"] = grouped["Mouse ID"].astype(int, errors='ignore')  # Mouse ID looks like string IDs, keep as is if cannot convert
grouped["Tumor Volume (mm3)"] = grouped["Tumor Volume (mm3)"].round().astype(int)
grouped["SEM of Metastatic Sites"] = grouped["SEM of Metastatic Sites"].fillna(0).round().astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_81/target_multisource_mcts.csv", index=False)