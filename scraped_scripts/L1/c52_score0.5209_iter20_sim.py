import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_52/training_0.csv", index_col=0)
df_unpivot = df0.melt(id_vars=["condition"], value_vars=["click"], var_name=None, value_name="0")
df_unpivot["0"] = df_unpivot["0"].astype(int)
df_unpivot["condition"] = df_unpivot["condition"].astype(int)
df_unpivot = df_unpivot[["condition", "0"]]
df_unpivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_52/target_multisource_mcts.csv", index=False)