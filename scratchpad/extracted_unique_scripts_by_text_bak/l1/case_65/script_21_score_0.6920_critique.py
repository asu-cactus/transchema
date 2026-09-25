import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_65/training_0.csv", index_col=0)
# Filter out rows where year is NaN or zero (if any)
df0 = df0[df0['year'].notna()]
df0 = df0[df0['year'] != 0]

result = df0.groupby("year", as_index=False).agg({"movie_id": "count"})
result.columns = ["year", "0"]
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)