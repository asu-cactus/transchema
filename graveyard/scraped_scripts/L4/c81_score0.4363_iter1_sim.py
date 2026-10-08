import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_1.csv", index_col=0)

merged = pd.merge(source0, source1, on="Mouse ID")

merged = merged.rename(columns={
    "Metastatic Sites": "Mean of Metastatic Sites",
    "Mouse ID": "Mouse ID",
    "Drug": "Drug",
    "Timepoint": "Timepoint",
    "Tumor Volume (mm3)": "Tumor Volume (mm3)"
})

merged["Timepoint"] = merged["Timepoint"].astype(int)
merged["Mean of Metastatic Sites"] = merged["Mean of Metastatic Sites"].astype(float)
merged["Mouse ID"] = merged["Mouse ID"].astype(str)
merged["Drug"] = merged["Drug"].astype(str)
merged["Tumor Volume (mm3)"] = merged["Tumor Volume (mm3)"].round().astype(int)

# SEM of Metastatic Sites is not present in sources, fill with 0 as integer (or NaN if preferred)
merged["SEM of Metastatic Sites"] = 0

merged = merged[["Drug", "Timepoint", "Mean of Metastatic Sites", "Mouse ID", "Tumor Volume (mm3)", "SEM of Metastatic Sites"]]

merged.to_csv("autopipeline-benchmarks/github-pipelines/length4_81/target_multisource_mcts.csv", index=False)