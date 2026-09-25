import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_72/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_72/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_72/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_72/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_72/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_72/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_72/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_72/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_72/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_72/training_9.csv", index_col=0)

# List of tables with the same schema to union
union_tables = [s0, s1, s3, s4, s5, s6, s7, s8, s9]

# Align columns for union: s5 has extra columns '5040' and '100.00%', drop them to match others
for i, df in enumerate(union_tables):
    if '5040' in df.columns:
        df.drop(columns=['5040', '100.00%'], inplace=True)

# Union all tables with the same schema
unioned = pd.concat(union_tables, ignore_index=True)

# Join unioned table with s2 on bid_id = sampled_bid_id
result = pd.merge(unioned, s2, how='inner', left_on='bid_id', right_on='sampled_bid_id')

# Drop sampled_bid_id as it's redundant
result.drop(columns=['sampled_bid_id'], inplace=True)

# Write output with exact column names as in target schema
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_72/target_multisource_mcts.csv", index=False)