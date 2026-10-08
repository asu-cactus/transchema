import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_1.csv", index_col=0)

# Join on Mouse ID
df = pd.merge(df0, df1, on="Mouse ID", how="inner")

# Group by Drug and Timepoint
grouped = df.groupby(["Drug", "Timepoint"])

# Aggregations
mean_metastatic = grouped["Metastatic Sites"].mean()
sem_metastatic = grouped["Metastatic Sites"].sem()
count_mouse = grouped["Mouse ID"].nunique()
mean_tumor_volume = grouped["Tumor Volume (mm3)"].mean()

# Build result DataFrame
result = pd.DataFrame({
    "Drug": mean_metastatic.index.get_level_values("Drug"),
    "Timepoint": mean_metastatic.index.get_level_values("Timepoint").astype(int),
    "Mean of Metastatic Sites": mean_metastatic.values,
    "Mouse ID": count_mouse.values.astype(int),
    "Tumor Volume (mm3)": np.round(mean_tumor_volume.values).astype(int),
    "SEM of Metastatic Sites": np.round(sem_metastatic.values).astype(int)
})

# Reorder columns to match target schema exactly
result = result[["Drug", "Timepoint", "Mean of Metastatic Sites", "Mouse ID", "Tumor Volume (mm3)", "SEM of Metastatic Sites"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_81/target_multisource_mcts.csv", index=False)