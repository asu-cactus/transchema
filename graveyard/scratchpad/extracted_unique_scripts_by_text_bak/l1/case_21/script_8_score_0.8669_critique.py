import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_21/training_0.csv", index_col=0)

# Filter out rows with null Major_category or Median
df0 = df0[df0["Major_category"].notnull() & df0["Median"].notnull()]

# Strip whitespace from Major_category
df0["Major_category"] = df0["Major_category"].str.strip()

# Group by Major_category and compute mean of Median
result = df0.groupby("Major_category", as_index=False)["Median"].mean()

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_21/target_multisource_mcts.csv", index=False)