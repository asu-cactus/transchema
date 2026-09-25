import pandas as pd

source_path = "autopipeline-benchmarks/github-pipelines/length1_4/training_0.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_4/target_multisource_mcts.csv"

df = pd.read_csv(source_path, index_col=0)

joined = pd.merge(df, df, on="fname")

result = joined.groupby("fname").size().reset_index(name="count_of_obs")
result["fname"] = result["fname"].astype(str)
result["count_of_obs"] = result["count_of_obs"].astype(int)

result.to_csv(target_path, index=False)