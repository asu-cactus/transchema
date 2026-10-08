import pandas as pd

# Read all source CSVs
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_3.csv", index_col=0)

# Union all sources
union_all = pd.concat([s0, s1, s2, s3], ignore_index=True)

# Group by key columns and sum numeric columns
group_cols = ['SubjectId', 'Split', 'Subject']
agg_cols = ['PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']

final = union_all.groupby(group_cols, as_index=False)[agg_cols].sum()

# Ensure correct dtypes as per target schema (all int)
final['SubjectId'] = final['SubjectId'].astype(int)
final['Split'] = final['Split'].astype(int)
final['Subject'] = final['Subject'].astype(int)
for c in agg_cols:
    final[c] = final[c].astype(int)

# Write output
final.to_csv("autopipeline-benchmarks/github-pipelines/length4_96/target_multisource_mcts.csv", index=False)