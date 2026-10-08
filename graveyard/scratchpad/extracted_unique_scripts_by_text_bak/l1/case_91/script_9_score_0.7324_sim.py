import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_91/training_0.csv", index_col=0)

group_cols = ['Name', 'Position', 'Age', 'Team_from', 'League_from', 'Team_to', 'League_to', 'Season']

agg_df = df0.groupby(group_cols).agg({
    'Transfer_fee': ['max', 'min'],
    'Market_value': ['max', 'min']
}).reset_index()

agg_df.columns = group_cols + ['Transfer_fee_max', 'Transfer_fee_min', 'Market_value_max', 'Market_value_min']

agg_df['Transfer_fee'] = agg_df['Transfer_fee_max'].combine_first(agg_df['Transfer_fee_min']).astype('Int64')
agg_df['Market_value'] = agg_df['Market_value_max'].combine_first(agg_df['Market_value_min']).astype(float)

result = agg_df[group_cols + ['Market_value', 'Transfer_fee']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_91/target_multisource_mcts.csv", index=False)