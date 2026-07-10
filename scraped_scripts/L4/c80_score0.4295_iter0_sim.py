import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_80/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_80/training_1.csv", index_col=0)

joined = pd.merge(df0, df1, on="Mouse ID", how="inner")

grouped = joined.groupby(["Drug", "Timepoint", "Mouse ID", "Metastatic Sites"], as_index=False).agg(
    **{
        "Mean of Tumor Volume (mm3)": ("Tumor Volume (mm3)", "mean"),
        "SEM of Tumor Volume (mm3)": ("Tumor Volume (mm3)", lambda x: x.std(ddof=1) / np.sqrt(len(x)) if len(x) > 1 else 0)
    }
)

grouped["Drug"] = grouped["Drug"].astype(str)
grouped["Timepoint"] = grouped["Timepoint"].astype(int)
grouped["Mouse ID"] = grouped["Mouse ID"].astype(int, errors='ignore')  # Mouse ID looks like string, keep as is if cannot convert
grouped["SEM of Tumor Volume (mm3)"] = grouped["SEM of Tumor Volume (mm3)"].round().astype(int)
grouped["Metastatic Sites"] = grouped["Metastatic Sites"].astype(int)

grouped = grouped[["Drug", "Timepoint", "Mean of Tumor Volume (mm3)", "Mouse ID", "SEM of Tumor Volume (mm3)", "Metastatic Sites"]]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_80/target_multisource_mcts.csv", index=False)