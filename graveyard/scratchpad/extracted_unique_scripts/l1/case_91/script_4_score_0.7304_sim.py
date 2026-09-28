import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_91/training_0.csv", index_col=0)

group_cols = ['Name', 'Position', 'Age', 'Team_from', 'League_from', 'Team_to', 'League_to', 'Season']
agg_dict = {
    'Market_value': 'sum',
    'Transfer_fee': 'count'
}

df_grouped = df0.groupby(group_cols, dropna=False).agg(agg_dict).reset_index()

df_grouped['Age'] = df_grouped['Age'].astype('Int64')
df_grouped['Transfer_fee'] = df_grouped['Transfer_fee'].astype('Int64')
df_grouped['Market_value'] = df_grouped['Market_value'].astype(float)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_91/target_multisource_mcts.csv", index=False)