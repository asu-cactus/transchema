import pandas as pd
import numpy as np

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_91/training_0.csv", index_col=0)

group_cols = ['Position', 'Team_from', 'League_from', 'Team_to', 'League_to', 'Season']

agg_df = df.groupby(group_cols).agg(
    Name_count=('Name', 'count'),
    Age_avg=('Age', 'mean'),
    Market_value_avg=('Market_value', 'mean'),
    Transfer_fee_avg=('Transfer_fee', 'mean')
).reset_index()

agg_df['Name'] = np.nan
agg_df['Age'] = agg_df['Age_avg'].round().astype('Int64')
agg_df['Market_value'] = agg_df['Market_value_avg']
agg_df['Transfer_fee'] = agg_df['Transfer_fee_avg'].round().astype('Int64')

result = agg_df[['Name', 'Position', 'Age', 'Team_from', 'League_from', 'Team_to', 'League_to', 'Season', 'Market_value', 'Transfer_fee']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_91/target_multisource_mcts.csv", index=False)