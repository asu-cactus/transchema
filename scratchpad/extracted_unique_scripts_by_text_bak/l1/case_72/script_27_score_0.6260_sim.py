import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_72/training_0.csv", index_col=0)
df_unpivot = df0.melt(id_vars=["condition"], value_vars=["click"], var_name="variable", value_name="0")
df_result = df_unpivot[["condition", "0"]].copy()
df_result["0"] = df_result["0"].astype(int)
df_result["condition"] = df_result["condition"].astype(int)
df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_72/target_multisource_mcts.csv", index=False)