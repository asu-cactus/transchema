import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_84/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_84/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_84/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_84/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length4_84/training_4.csv"
]

dfs = []
for p in paths:
    df = pd.read_csv(p, index_col=0)
    # Filter out rows where 'age_grp' is not a valid age group (remove header/summary rows)
    # Valid age_grp values are strings like '0-1', '1-4', '5-9', '10-14', '15-17', etc.
    # Remove rows where 'age_grp' is 'Year', 'Total for selection', or any non-age group string
    # We keep rows where 'age_grp' is not null and does not contain 'Year' or 'Total'
    df = df[~df['age_grp'].isin(['Year', 'Total for selection'])]
    dfs.append(df)

# Concatenate all cleaned dataframes
df_all = pd.concat(dfs, ignore_index=True)

# Select only the target columns in correct order
df_all = df_all[['age_grp', 'Count', 'Notes', 'Rate', 'Statistics']]

# Group by 'age_grp', 'Notes', 'Statistics' and aggregate Count by sum, Rate by mean
agg_df = df_all.groupby(['age_grp', 'Notes', 'Statistics'], dropna=False).agg({
    'Count': 'sum',
    'Rate': 'mean'
}).reset_index()

# Write to CSV
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_84/target_multisource_mcts.csv", index=False)