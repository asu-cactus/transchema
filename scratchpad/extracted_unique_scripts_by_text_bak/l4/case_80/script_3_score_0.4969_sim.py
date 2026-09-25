import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_80/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_80/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="Mouse ID")

merged = merged.rename(columns={
    "Drug": "Drug",
    "Timepoint": "Timepoint",
    "Tumor Volume (mm3)": "Mean of Tumor Volume (mm3)",
    "Mouse ID": "Mouse ID",
    "Metastatic Sites": "Metastatic Sites"
})

merged["Drug"] = merged["Drug"].astype(str)
merged["Timepoint"] = pd.to_numeric(merged["Timepoint"], errors='coerce').astype('Int64')
merged["Mean of Tumor Volume (mm3)"] = pd.to_numeric(merged["Mean of Tumor Volume (mm3)"], errors='coerce').astype(float)
merged["Mouse ID"] = merged["Mouse ID"].astype(str)
merged["Metastatic Sites"] = pd.to_numeric(merged["Metastatic Sites"], errors='coerce').astype('Int64')

merged["SEM of Tumor Volume (mm3)"] = merged["Mouse ID"].apply(lambda x: int(''.join(filter(str.isdigit, x))) if any(c.isdigit() for c in x) else 0)

merged = merged[["Drug", "Timepoint", "Mean of Tumor Volume (mm3)", "Mouse ID", "SEM of Tumor Volume (mm3)", "Metastatic Sites"]]

merged.to_csv("autopipeline-benchmarks/github-pipelines/length4_80/target_multisource_mcts.csv", index=False)