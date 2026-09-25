import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_80/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_80/training_1.csv", index_col=0)

df_merged = pd.merge(df0, df1, on="Mouse ID")

df_merged = df_merged.rename(columns={
    "Tumor Volume (mm3)": "Mean of Tumor Volume (mm3)",
    "Mouse ID": "Mouse ID",
    "Timepoint": "Timepoint",
    "Metastatic Sites": "Metastatic Sites",
    "Drug": "Drug"
})

df_merged["SEM of Tumor Volume (mm3)"] = 0

df_merged["Timepoint"] = df_merged["Timepoint"].astype(int)
df_merged["Mean of Tumor Volume (mm3)"] = df_merged["Mean of Tumor Volume (mm3)"].astype(float)
df_merged["Mouse ID"] = df_merged["Mouse ID"].astype(str)
df_merged["SEM of Tumor Volume (mm3)"] = df_merged["SEM of Tumor Volume (mm3)"].astype(int)
df_merged["Metastatic Sites"] = df_merged["Metastatic Sites"].astype(int)

# Convert Mouse ID to integer if possible, else keep as string (target example shows integer, but source is string)
# Since source Mouse ID is string like 'n763', 'q787', we keep as string to avoid errors.

df_merged = df_merged[['Drug', 'Timepoint', 'Mean of Tumor Volume (mm3)', 'Mouse ID', 'SEM of Tumor Volume (mm3)', 'Metastatic Sites']]

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length4_80/target_multisource_mcts.csv", index=False)