import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_8/training_1.csv", index_col=0)

df0_unpivot = df0.melt(id_vars=["Mouse ID", "Timepoint"], value_vars=["Tumor Volume (mm3)", "Metastatic Sites"], var_name="Drug", value_name="Value")

df_merged = pd.merge(df0_unpivot, df1, on="Mouse ID", how="inner")

result = df_merged[["Drug_y", "Timepoint", "Mouse ID"]].rename(columns={"Drug_y": "Drug"})

result["Timepoint"] = result["Timepoint"].astype(int)
result["Mouse ID"] = result["Mouse ID"].apply(lambda x: int(''.join(filter(str.isdigit, str(x)))) if pd.notnull(x) else x)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_8/target_multisource_mcts.csv", index=False)