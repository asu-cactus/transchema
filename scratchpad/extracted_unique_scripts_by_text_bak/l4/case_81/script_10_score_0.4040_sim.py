import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_1.csv", index_col=0)

merged = pd.merge(source0, source1, on="Mouse ID")

merged["Drug"] = merged["Drug"].astype(str)
merged["Timepoint"] = merged["Timepoint"].astype(int)
merged["Mean of Metastatic Sites"] = merged["Metastatic Sites"].astype(float)
merged["Mouse ID"] = merged["Mouse ID"].str.extract('(\d+)').astype(int)
merged["Tumor Volume (mm3)"] = merged["Tumor Volume (mm3)"].round().astype(int)
merged["SEM of Metastatic Sites"] = merged["Metastatic Sites"].round().astype(int)

result = merged[["Drug", "Timepoint", "Mean of Metastatic Sites", "Mouse ID", "Tumor Volume (mm3)", "SEM of Metastatic Sites"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_81/target_multisource_mcts.csv", index=False)