import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_91/training_0.csv", index_col=0)

group_cols = ['Name', 'Position', 'Age', 'Team_from', 'League_from', 'Team_to', 'League_to', 'Season']
agg_dict = {
    'Market_value': 'mean',
    'Transfer_fee': 'mean'
}

result = df0.groupby(group_cols, dropna=False).agg(agg_dict).reset_index()

result['Age'] = result['Age'].astype('Int64')
result['Transfer_fee'] = result['Transfer_fee'].round().astype('Int64')
result['Market_value'] = result['Market_value'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_91/target_multisource_mcts.csv", index=False)