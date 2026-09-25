import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_1.csv", index_col=0)

merged = pd.merge(df1, df0, on="Mouse ID")

grouped = merged.groupby(["Drug", "Timepoint", "Mouse ID"], as_index=False).agg(
    {
        "Metastatic Sites": ["mean", "sem"],
        "Tumor Volume (mm3)": "mean"
    }
)

grouped.columns = ["Drug", "Timepoint", "Mouse ID", "Mean of Metastatic Sites", "SEM of Metastatic Sites", "Tumor Volume (mm3)"]

grouped["Timepoint"] = grouped["Timepoint"].astype(int)
grouped["Mouse ID"] = grouped["Mouse ID"].apply(lambda x: int(''.join(filter(str.isdigit, str(x)))) if any(c.isdigit() for c in str(x)) else np.nan)
grouped["Tumor Volume (mm3)"] = grouped["Tumor Volume (mm3)"].round().astype(int)
grouped["Mean of Metastatic Sites"] = grouped["Mean of Metastatic Sites"].astype(float)
grouped["SEM of Metastatic Sites"] = grouped["SEM of Metastatic Sites"].fillna(0).round().astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_81/target_multisource_mcts.csv", index=False)