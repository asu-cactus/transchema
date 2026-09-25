import pandas as pd
import numpy as np

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_80/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_80/training_1.csv", index_col=0)

# Convert Mouse ID in both tables to string (already string, but ensure)
df0["Mouse ID"] = df0["Mouse ID"].astype(str)
df1["Mouse ID"] = df1["Mouse ID"].astype(str)

# Join on Mouse ID
merged = pd.merge(df0, df1, on="Mouse ID", how="inner")

# Rename columns to target schema names
merged = merged.rename(columns={
    "Drug": "Drug",
    "Timepoint": "Timepoint",
    "Tumor Volume (mm3)": "Mean of Tumor Volume (mm3)",
    "Mouse ID": "Mouse ID",
    "Metastatic Sites": "Metastatic Sites"
})

# Convert types according to target schema
merged["Drug"] = merged["Drug"].astype(str)
merged["Timepoint"] = pd.to_numeric(merged["Timepoint"], errors='coerce').astype(int)
merged["Mean of Tumor Volume (mm3)"] = pd.to_numeric(merged["Mean of Tumor Volume (mm3)"], errors='coerce').astype(float)
# Convert Mouse ID to integer by extracting digits only
merged["Mouse ID"] = merged["Mouse ID"].str.extract('(\d+)').astype(int)
merged["Metastatic Sites"] = pd.to_numeric(merged["Metastatic Sites"], errors='coerce').astype(int)

# Define a function to calculate SEM (standard error of mean)
def sem(x):
    return x.std(ddof=1) / np.sqrt(len(x)) if len(x) > 1 else 0

# Group by Drug, Timepoint, Mouse ID
grouped = merged.groupby(["Drug", "Timepoint", "Mouse ID"], as_index=False).agg({
    "Mean of Tumor Volume (mm3)": "mean",
    "Metastatic Sites": "mean"
})

# Calculate SEM separately and merge
sem_df = merged.groupby(["Drug", "Timepoint", "Mouse ID"])["Mean of Tumor Volume (mm3)"].agg(sem).reset_index()
sem_df = sem_df.rename(columns={"Mean of Tumor Volume (mm3)": "SEM of Tumor Volume (mm3)"})

# Merge SEM into grouped
result = pd.merge(grouped, sem_df, on=["Drug", "Timepoint", "Mouse ID"], how="left")

# Convert SEM and Metastatic Sites to integer as per target schema
result["SEM of Tumor Volume (mm3)"] = result["SEM of Tumor Volume (mm3)"].round().astype(int)
result["Metastatic Sites"] = result["Metastatic Sites"].round().astype(int)

# Reorder columns to match target schema
result = result[["Drug", "Timepoint", "Mean of Tumor Volume (mm3)", "Mouse ID", "SEM of Tumor Volume (mm3)", "Metastatic Sites"]]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_80/target_multisource_mcts.csv", index=False)