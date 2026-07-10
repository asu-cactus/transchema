import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_1.csv", index_col=0)

df = pd.merge(df0, df1, on="Mouse ID", how="inner")

grouped = df.groupby(["Drug", "Timepoint", "Mouse ID", "Tumor Volume (mm3)"])["Metastatic Sites"]
mean_metastatic = grouped.mean()
sem_metastatic = grouped.sem()

result = mean_metastatic.reset_index(name="Mean of Metastatic Sites")
result["SEM of Metastatic Sites"] = sem_metastatic.values

result["Timepoint"] = result["Timepoint"].astype(int)
result["Mouse ID"] = result["Mouse ID"].apply(lambda x: int(''.join(filter(str.isdigit, str(x)))) if any(c.isdigit() for c in str(x)) else np.nan).astype("Int64")
result["Tumor Volume (mm3)"] = result["Tumor Volume (mm3)"].round().astype("Int64")
result["SEM of Metastatic Sites"] = result["SEM of Metastatic Sites"].round().astype("Int64")

result = result[["Drug", "Timepoint", "Mean of Metastatic Sites", "Mouse ID", "Tumor Volume (mm3)", "SEM of Metastatic Sites"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_81/target_multisource_mcts.csv", index=False)