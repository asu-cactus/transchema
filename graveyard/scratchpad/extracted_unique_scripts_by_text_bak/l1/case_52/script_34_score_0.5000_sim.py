import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_52/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, on="condition", suffixes=('_x', '_y'))

df_unpivot = df_joined.melt(id_vars=["condition"], value_vars=["click_x", "click_y"], var_name="variable", value_name="0")

df_result = df_unpivot[["condition", "0"]]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_52/target_multisource_mcts.csv", index=False)