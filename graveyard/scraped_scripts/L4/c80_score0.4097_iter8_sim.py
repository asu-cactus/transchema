import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_80/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_80/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="Mouse ID")

grouped = merged.groupby(["Drug", "Timepoint", "Mouse ID"], as_index=False).agg(
    **{
        "Mean of Tumor Volume (mm3)": ("Tumor Volume (mm3)", "mean"),
        "SEM of Tumor Volume (mm3)": ("Tumor Volume (mm3)", lambda x: np.std(x, ddof=1) / np.sqrt(len(x)) if len(x) > 1 else 0),
        "Metastatic Sites": ("Metastatic Sites", "sum"),
    }
)

grouped["Timepoint"] = grouped["Timepoint"].astype(int)
grouped["Mouse ID"] = grouped["Mouse ID"].apply(lambda x: int(''.join(filter(str.isdigit, str(x)))) if any(c.isdigit() for c in str(x)) else np.nan)
grouped["SEM of Tumor Volume (mm3)"] = grouped["SEM of Tumor Volume (mm3)"].round().astype(int)

grouped = grouped[["Drug", "Timepoint", "Mean of Tumor Volume (mm3)", "Mouse ID", "SEM of Tumor Volume (mm3)", "Metastatic Sites"]]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_80/target_multisource_mcts.csv", index=False)