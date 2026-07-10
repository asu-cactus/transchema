import pandas as pd

s0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_38/training_0.csv', index_col=0)
s1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_38/training_1.csv', index_col=0)
s2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_38/training_2.csv', index_col=0)
s3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_38/training_3.csv', index_col=0)

union_01 = pd.concat([s0, s1], ignore_index=True)

join_01_2 = pd.merge(union_01, s2, on='batsman', how='inner')

final_join = pd.merge(join_01_2, s3, on='batsman', how='inner')

final_join['batsman_runs'] = 0

final_join = final_join.rename(columns={
    'batsman_runs_x': 'batsman_runs_x',
    'total_runs': 'total_runs',
    'batsman_runs_y': 'batsman_runs_y',
    'batsman_runs': 'batsman_runs'
})

final_join = final_join[['batsman', 'batsman_runs_x', 'total_runs', 'batsman_runs_y', 'batsman_runs']]

final_join['batsman_runs_x'] = final_join['batsman_runs_x'].astype(float)
final_join['total_runs'] = final_join['total_runs'].astype(int)
final_join['batsman_runs_y'] = final_join['batsman_runs_y'].astype(float)
final_join['batsman_runs'] = final_join['batsman_runs'].astype(int)

final_join.to_csv('autopipeline-benchmarks/github-pipelines/length3_38/target_multisource_mcts.csv', index=False)