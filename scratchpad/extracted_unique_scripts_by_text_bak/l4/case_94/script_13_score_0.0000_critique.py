import pandas as pd

# Read all source CSVs with index_col=0 to ignore the first numerical index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_3.csv", index_col=0)

# UNION all source tables (concatenate)
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Group by the leftmost columns of the target schema that are string or integer and unique
group_cols = ['Split', 'SubjectId', 'Subject']

# Aggregate by summing the numeric columns
agg_cols = ['PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']

result = df_all.groupby(group_cols, as_index=False)[agg_cols].sum()

# Ensure correct dtypes as per target schema
result = result.astype({
    'Split': str,
    'SubjectId': int,
    'Subject': int,
    'PA': int,
    'AB': int,
    'H': int,
    'TB': int,
    'BB': int,
    'SF': int,
    'HBP': int
})

# Write the final output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_94/target_multisource_mcts.csv", index=False)