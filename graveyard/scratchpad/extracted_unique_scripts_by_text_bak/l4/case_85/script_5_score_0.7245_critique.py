import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length4_85/training_0.csv"

df0 = pd.read_csv(source0_path, index_col=0)

df_grouped = df0.groupby("crit_cn", as_index=False).agg({"critic": "count"})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_85/target_multisource_mcts.csv", index=False)