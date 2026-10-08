import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_72/training_0.csv", index_col=0)

df0["click"] = df0["click"].astype(int)

df_result = df0.groupby("condition", as_index=False)["click"].sum()

df_result.rename(columns={"click": "0"}, inplace=True)

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_72/target_multisource_mcts.csv", index=False)