import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_4.csv", index_col=0)

join_0 = pd.merge(s2, s3, on="batsman", how="inner", suffixes=('_x', '_y'))
join_1 = pd.merge(s0, s1, on="batsman", how="inner", suffixes=('_x', '_y'))
join_2 = pd.merge(join_0, join_1, on="batsman", how="inner")
final = pd.merge(join_2, s4, on="batsman", how="inner", suffixes=('_x', '_y'))

final = final.rename(columns={
    'batsman_runs_x': 'batsman_runs_x',
    'total_runs_x': 'total_runs_x',
    'total_runs_y': 'total_runs_y',
    'batsman_runs_y': 'batsman_runs_y',
    'batsman_runs': 'batsman_runs'
})

final = final[['batsman', 'batsman_runs_x', 'total_runs_x', 'total_runs_y', 'batsman_runs_y', 'batsman_runs']]

final['batsman_runs_x'] = final['batsman_runs_x'].astype(float)
final['total_runs_x'] = final['total_runs_x'].astype(int)
final['total_runs_y'] = final['total_runs_y'].astype(int)
final['batsman_runs_y'] = final['batsman_runs_y'].astype(int)
final['batsman_runs'] = final['batsman_runs'].astype(int)

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_33/target_multisource_mcts.csv", index=False)