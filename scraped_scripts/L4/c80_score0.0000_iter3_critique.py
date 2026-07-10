import pandas as pd
import numpy as np

source0_path = "autopipeline-benchmarks/github-pipelines/length4_80/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length4_80/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length4_80/target_multisource_mcts.csv"

# Read sources with index_col=0 as instructed
df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Convert Mouse ID to consistent type for join
# Source0 Mouse ID is string, target expects integer, so try to convert
# If Mouse ID cannot be converted to int, keep as string (but target shows int)
# We'll try to convert both to string first, then convert to int after join if possible

df0["Mouse ID"] = df0["Mouse ID"].astype(str)
df1["Mouse ID"] = df1["Mouse ID"].astype(str)

# Join on Mouse ID
df_merged = pd.merge(df0, df1, on="Mouse ID", how="inner")

# Convert columns to proper types
df_merged["Drug"] = df_merged["Drug"].astype(str)
df_merged["Timepoint"] = pd.to_numeric(df_merged["Timepoint"], errors='coerce').astype('Int64')
df_merged["Tumor Volume (mm3)"] = pd.to_numeric(df_merged["Tumor Volume (mm3)"], errors='coerce').astype(float)
df_merged["Metastatic Sites"] = pd.to_numeric(df_merged["Metastatic Sites"], errors='coerce').astype('Int64')

# Convert Mouse ID to integer if possible (target expects integer)
# If conversion fails, keep as string (but target examples show integer)
# We'll try to convert, dropping rows where conversion fails
df_merged["Mouse ID"] = pd.to_numeric(df_merged["Mouse ID"], errors='coerce').astype('Int64')

# Drop rows with NaN in group by columns or aggregation columns to avoid errors
df_merged = df_merged.dropna(subset=["Drug", "Timepoint", "Mouse ID", "Tumor Volume (mm3)", "Metastatic Sites"])

# Define aggregation functions
def sem(x):
    return x.std(ddof=1) / np.sqrt(len(x)) if len(x) > 1 else 0.0

agg_df = df_merged.groupby(["Drug", "Timepoint", "Mouse ID"], as_index=False).agg(
    **{
        "Mean of Tumor Volume (mm3)": ("Tumor Volume (mm3)", "mean"),
        "SEM of Tumor Volume (mm3)": ("Tumor Volume (mm3)", sem),
        "Metastatic Sites": ("Metastatic Sites", "mean"),
    }
)

# Convert Metastatic Sites to integer as in target schema
agg_df["Metastatic Sites"] = agg_df["Metastatic Sites"].round().astype('Int64')

# Ensure types match target schema
agg_df["Drug"] = agg_df["Drug"].astype(str)
agg_df["Timepoint"] = agg_df["Timepoint"].astype('Int64')
agg_df["Mouse ID"] = agg_df["Mouse ID"].astype('Int64')
agg_df["Mean of Tumor Volume (mm3)"] = agg_df["Mean of Tumor Volume (mm3)"].astype(float)
agg_df["SEM of Tumor Volume (mm3)"] = agg_df["SEM of Tumor Volume (mm3)"].astype(float)

# Reorder columns to match target schema
result = agg_df[["Drug", "Timepoint", "Mean of Tumor Volume (mm3)", "Mouse ID", "SEM of Tumor Volume (mm3)", "Metastatic Sites"]]

result.to_csv(target_path, index=False)