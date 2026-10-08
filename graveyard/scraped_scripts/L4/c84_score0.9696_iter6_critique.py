import pandas as pd

# Read all source files with index_col=0 to ignore the first numerical index column
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_4.csv", index_col=0)

# All source tables have the same schema: ['age_grp', 'Count', 'Notes', 'Rate', 'Statistics']
# Concatenate all source tables vertically (UNION)
df_all = pd.concat([s0, s1, s2, s3, s4], ignore_index=True)

# Remove rows that are header or metadata rows:
# These rows often have 'age_grp' or 'Statistics' columns containing strings like 'Year', 'County', or other non-data values.
# We keep rows where 'age_grp' is not null and does not equal 'Year' or similar header values,
# and where 'Statistics' is not null and does not equal 'County' or similar header values.

# Convert columns to string for safe comparison
age_grp_str = df_all['age_grp'].astype(str).str.strip().str.lower()
statistics_str = df_all['Statistics'].astype(str).str.strip().str.lower()

# Filter conditions: exclude rows where age_grp or Statistics are header-like
mask = (~age_grp_str.isin(['year', 'total for selection', 'unnamed: 1'])) & (~statistics_str.isin(['county', '']))

df_all = df_all[mask]

# Reset index after filtering
df_all = df_all.reset_index(drop=True)

# Ensure columns are in the target schema order and names exactly
df_all = df_all[['age_grp', 'Count', 'Notes', 'Rate', 'Statistics']]

# Write to output CSV without index
df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_84/target_multisource_mcts.csv", index=False)