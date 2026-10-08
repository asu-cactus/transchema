import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_91/training_0.csv", index_col=0)

group_cols = ['Name', 'Position', 'Age', 'Team_from', 'League_from', 'Team_to', 'League_to', 'Season']
agg_cols = ['Market_value', 'Transfer_fee']

df_grouped = df0.groupby(group_cols, dropna=False, as_index=False).agg({
    'Market_value': 'mean',
    'Transfer_fee': 'mean'
})

df_grouped['Age'] = df_grouped['Age'].astype('Int64')
df_grouped['Transfer_fee'] = df_grouped['Transfer_fee'].round().astype('Int64')
df_grouped['Market_value'] = df_grouped['Market_value'].astype(float)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_91/target_multisource_mcts.csv", index=False)