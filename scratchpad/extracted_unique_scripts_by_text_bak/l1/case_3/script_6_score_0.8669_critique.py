import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_3/training_0.csv", index_col=0)

# Normalize Major_category by stripping spaces
df0["Major_category"] = df0["Major_category"].str.strip()

# Group by Major_category and take mean of Median
result = df0.groupby("Major_category", as_index=False)["Median"].mean()

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_3/target_multisource_mcts.csv", index=False)