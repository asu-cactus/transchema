import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_3/training_0.csv", index_col=0)

# The partial plan suggests joining Source1_3_0 with itself on Major_category, which is redundant and unnecessary.
# Since only one source table exists, and the target requires grouping by Major_category and median of Median,
# we can directly group by Major_category and compute the median of the Median column.

result = df0.groupby("Major_category", as_index=False)["Median"].median()

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_3/target_multisource_mcts.csv", index=False)