import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_80/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_80/training_1.csv", index_col=0)

df = pd.merge(df0, df1, on="Mouse ID")

df = df.rename(columns={
    "Tumor Volume (mm3)": "Mean of Tumor Volume (mm3)",
    "Mouse ID": "Mouse ID",
    "Timepoint": "Timepoint",
    "SEM of Tumor Volume (mm3)": "SEM of Tumor Volume (mm3)",
    "Metastatic Sites": "Metastatic Sites",
    "Drug": "Drug"
})

# The source 0 does not have SEM of Tumor Volume (mm3), so we need to create it.
# The target schema requires SEM of Tumor Volume (mm3) as integer.
# Since no source column for SEM is given, we will create it as integer 0 (or NaN).
# But the target examples show SEM values equal to Mouse ID or Metastatic Sites, which is suspicious.
# The prompt does not mention SEM in source, so we create SEM column as integer 0.

df["SEM of Tumor Volume (mm3)"] = 0

df = df[["Drug", "Timepoint", "Mean of Tumor Volume (mm3)", "Mouse ID", "SEM of Tumor Volume (mm3)", "Metastatic Sites"]]

df["Drug"] = df["Drug"].astype(str)
df["Timepoint"] = pd.to_numeric(df["Timepoint"], errors='coerce').astype('Int64')
df["Mean of Tumor Volume (mm3)"] = pd.to_numeric(df["Mean of Tumor Volume (mm3)"], errors='coerce').astype(float)
df["Mouse ID"] = pd.to_numeric(df["Mouse ID"].str.extract('(\d+)')[0], errors='coerce').astype('Int64')
df["SEM of Tumor Volume (mm3)"] = pd.to_numeric(df["SEM of Tumor Volume (mm3)"], errors='coerce').astype('Int64')
df["Metastatic Sites"] = pd.to_numeric(df["Metastatic Sites"], errors='coerce').astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_80/target_multisource_mcts.csv", index=False)