import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_91/training_0.csv", index_col=0)

group_cols = ['Name', 'Position', 'Age', 'Team_from', 'League_from', 'Team_to', 'League_to', 'Season']

agg_df = df.groupby(group_cols).agg(
    Market_value=('Market_value', 'min'),
    Transfer_fee=('Transfer_fee', 'max')
).reset_index()

agg_df['Age'] = agg_df['Age'].astype('Int64')
agg_df['Transfer_fee'] = agg_df['Transfer_fee'].astype('Int64')
agg_df['Market_value'] = agg_df['Market_value'].astype(float)
agg_df['Position'] = agg_df['Position'].astype(str)
agg_df['Name'] = agg_df['Name'].astype(str)
agg_df['Team_from'] = agg_df['Team_from'].astype(str)
agg_df['League_from'] = agg_df['League_from'].astype(str)
agg_df['Team_to'] = agg_df['Team_to'].astype(str)
agg_df['League_to'] = agg_df['League_to'].astype(str)
agg_df['Season'] = agg_df['Season'].astype(str)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_91/target_multisource_mcts.csv", index=False)