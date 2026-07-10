import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_24/training_0.csv", index_col=0)

df_union = pd.concat([df0], ignore_index=True)

result = df_union.groupby("condition", as_index=False)["click"].sum()

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_24/target_multisource_mcts.csv", index=False)