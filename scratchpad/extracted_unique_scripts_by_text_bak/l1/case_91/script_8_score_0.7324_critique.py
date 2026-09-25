import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_91/training_0.csv", index_col=0)

# Ensure correct types
df0['Name'] = df0['Name'].astype(str)
df0['Position'] = df0['Position'].astype(str)
df0['Age'] = pd.to_numeric(df0['Age'], errors='coerce').astype('Int64')
df0['Team_from'] = df0['Team_from'].astype(str)
df0['League_from'] = df0['League_from'].astype(str)
df0['Team_to'] = df0['Team_to'].astype(str)
df0['League_to'] = df0['League_to'].astype(str)
df0['Season'] = df0['Season'].astype(str)
df0['Market_value'] = pd.to_numeric(df0['Market_value'], errors='coerce').astype(float)
df0['Transfer_fee'] = pd.to_numeric(df0['Transfer_fee'], errors='coerce').astype('Int64')

# Since only one source, UNION is trivial (just df0)
# Group by the leftmost non-float columns (first 8 columns)
group_cols = ['Name', 'Position', 'Age', 'Team_from', 'League_from', 'Team_to', 'League_to', 'Season']

# Aggregate Market_value by mean, Transfer_fee by sum
agg_df = df0.groupby(group_cols, dropna=False).agg({
    'Market_value': 'mean',
    'Transfer_fee': 'sum'
}).reset_index()

# Ensure Transfer_fee is integer type after aggregation
agg_df['Transfer_fee'] = agg_df['Transfer_fee'].astype('Int64')

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_91/target_multisource_mcts.csv", index=False)