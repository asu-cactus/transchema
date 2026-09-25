import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_91/training_0.csv", index_col=0)

agg_df = df0.groupby(
    ['Position', 'Team_from', 'League_from', 'Team_to', 'League_to', 'Season'],
    dropna=False,
    as_index=False
).agg({
    'Transfer_fee': 'sum',
    'Age': 'mean',
    'Name': 'first',
    'Market_value': 'first'
})

agg_df['Age'] = agg_df['Age'].round().astype('Int64')
agg_df['Transfer_fee'] = agg_df['Transfer_fee'].round().astype('Int64')
agg_df['Market_value'] = agg_df['Market_value'].astype(float)
agg_df['Name'] = agg_df['Name'].astype(str)
agg_df['Position'] = agg_df['Position'].astype(str)
agg_df['Team_from'] = agg_df['Team_from'].astype(str)
agg_df['League_from'] = agg_df['League_from'].astype(str)
agg_df['Team_to'] = agg_df['Team_to'].astype(str)
agg_df['League_to'] = agg_df['League_to'].astype(str)
agg_df['Season'] = agg_df['Season'].astype(str)

agg_df = agg_df[['Name', 'Position', 'Age', 'Team_from', 'League_from', 'Team_to', 'League_to', 'Season', 'Market_value', 'Transfer_fee']]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_91/target_multisource_mcts.csv", index=False)