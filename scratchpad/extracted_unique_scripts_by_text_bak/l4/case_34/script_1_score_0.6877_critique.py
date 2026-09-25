import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_4.csv", index_col=0)

# Join source0 and source3 on batsman
joined_0_3 = pd.merge(source0, source3, on='batsman', how='inner', suffixes=('_x', '_y'))

# Join with source1 (total_runs), rename total_runs to total_runs_x
joined_0_3_1 = pd.merge(joined_0_3, source1, on='batsman', how='inner')
joined_0_3_1 = joined_0_3_1.rename(columns={'total_runs': 'total_runs_x'})

# Join with source4 (total_runs), rename total_runs to total_runs_y
joined_0_3_1_4 = pd.merge(joined_0_3_1, source4, on='batsman', how='inner')
joined_0_3_1_4 = joined_0_3_1_4.rename(columns={'total_runs': 'total_runs_y'})

# Join with source2 (has batsman_runs, no of balls, strike)
final_join = pd.merge(joined_0_3_1_4, source2, on='batsman', how='inner')

# Group by batsman and aggregate
agg_dict = {
    'total_runs_x': 'sum',
    'batsman_runs_x': 'sum',
    'batsman_runs_y': 'sum',
    'no of balls': 'sum',
    'batsman_runs': 'sum',
    'strike': 'mean',
    'total_runs_y': 'sum'
}

final = final_join.groupby('batsman', as_index=False).agg(agg_dict)

# Fill NaNs with 0 for integer columns after aggregation
int_cols = ['total_runs_x', 'batsman_runs_x', 'batsman_runs_y', 'no of balls', 'batsman_runs', 'total_runs_y']
final[int_cols] = final[int_cols].fillna(0).astype(int)

# strike is float, keep as is (mean aggregation)
final['strike'] = final['strike'].astype(float)

# Reorder columns exactly as target schema
final = final[['batsman', 'total_runs_x', 'batsman_runs_x', 'batsman_runs_y', 'no of balls', 'batsman_runs', 'strike', 'total_runs_y']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_34/target_multisource_mcts.csv", index=False)