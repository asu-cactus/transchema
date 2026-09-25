import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_3.csv", index_col=0)

# UNION all source tables
df = pd.concat([s0, s1, s2, s3], ignore_index=True)

# GROUP BY the leftmost columns (keys) and sum the numeric columns
group_cols = ["SubjectId", "Split", "Subject"]
agg_cols = ["PA", "AB", "H", "TB", "BB", "SF", "HBP"]

df = df.groupby(group_cols, as_index=False)[agg_cols].sum()

# Write output with exact target schema column names
df.to_csv("autopipeline-benchmarks/github-pipelines/length4_96/target_multisource_mcts.csv", index=False)