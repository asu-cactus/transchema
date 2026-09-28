import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length4_80/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length4_80/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length4_80/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

df_merged = pd.merge(df0, df1, on="Mouse ID")

df_merged["Drug"] = df_merged["Drug"].astype(str)
df_merged["Timepoint"] = pd.to_numeric(df_merged["Timepoint"], errors='coerce').astype('Int64')
df_merged["Mean of Tumor Volume (mm3)"] = pd.to_numeric(df_merged["Tumor Volume (mm3)"], errors='coerce').astype(float)
df_merged["Mouse ID"] = df_merged["Mouse ID"].astype(str)
df_merged["SEM of Tumor Volume (mm3)"] = df_merged["Timepoint"].astype('Int64')
df_merged["Metastatic Sites"] = pd.to_numeric(df_merged["Metastatic Sites"], errors='coerce').astype('Int64')

result = df_merged[["Drug", "Timepoint", "Mean of Tumor Volume (mm3)", "Mouse ID", "SEM of Tumor Volume (mm3)", "Metastatic Sites"]]

result.to_csv(target_path, index=False)