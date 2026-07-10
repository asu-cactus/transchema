import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_4/training_0.csv", index_col=0)

result = df0.groupby("fname", as_index=False).size().rename(columns={"size": "count_of_obs"})

result["fname"] = result["fname"].astype(str)
result["count_of_obs"] = result["count_of_obs"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_4/target_multisource_mcts.csv", index=False)