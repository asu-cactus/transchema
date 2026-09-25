import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_52/training_0.csv", index_col=0)

df_result = df0.groupby("condition", as_index=False).agg({"click": "sum"})

df_result.columns = ["condition", "0"]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_52/target_multisource_mcts.csv", index=False)