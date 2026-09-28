import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="Mouse ID", how="inner")

merged["Timepoint"] = merged["Timepoint"].astype(int)
merged["Tumor Volume (mm3)"] = merged["Tumor Volume (mm3)"].round().astype("Int64")
merged["Mean of Metastatic Sites"] = merged["Metastatic Sites"].astype(float)
merged["SEM of Metastatic Sites"] = merged["Metastatic Sites"].round().astype("Int64")
merged["Mouse ID"] = pd.to_numeric(merged["Mouse ID"], errors='coerce').astype("Int64")

result = merged.rename(columns={
    "Drug": "Drug",
    "Timepoint": "Timepoint",
    "Mean of Metastatic Sites": "Mean of Metastatic Sites",
    "Mouse ID": "Mouse ID",
    "Tumor Volume (mm3)": "Tumor Volume (mm3)",
    "SEM of Metastatic Sites": "SEM of Metastatic Sites"
})

result = result[["Drug", "Timepoint", "Mean of Metastatic Sites", "Mouse ID", "Tumor Volume (mm3)", "SEM of Metastatic Sites"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_81/target_multisource_mcts.csv", index=False)