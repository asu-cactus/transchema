import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_52/training_0.csv", index_col=0)
df_unpivoted = df0.melt(id_vars=["condition"], value_vars=["click"], var_name="variable", value_name="0")
df_unpivoted = df_unpivoted.drop(columns=["variable"])
df_unpivoted["0"] = df_unpivoted["0"].astype(int)
df_unpivoted["condition"] = df_unpivoted["condition"].astype(int)
df_unpivoted.to_csv("autopipeline-benchmarks/github-pipelines/length1_52/target_multisource_mcts.csv", index=False)