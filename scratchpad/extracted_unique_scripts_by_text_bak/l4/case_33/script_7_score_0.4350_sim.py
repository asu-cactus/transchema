import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_4.csv", index_col=0)

g4 = s4.groupby("batsman", as_index=False).agg(batsman_runs=('batsman_runs', 'mean'))
g0 = s0.groupby("batsman", as_index=False).agg(batsman_runs=('batsman_runs', 'mean'))
g1 = s1.groupby("batsman", as_index=False).agg(total_runs=('total_runs', 'sum'))
g2 = s2.groupby("batsman", as_index=False).agg(total_runs=('total_runs', 'sum'))
g3 = s3.groupby("batsman", as_index=False).agg(batsman_runs=('batsman_runs', 'sum'))

j40 = pd.merge(g4, g0, on="batsman", how="outer", suffixes=('_y', '_x'))
j401 = pd.merge(j40, g1, on="batsman", how="outer")
j4012 = pd.merge(j401, g2, on="batsman", how="outer", suffixes=('_x', '_y'))
final = pd.merge(j4012, g3, on="batsman", how="outer")

final = final.rename(columns={
    'batsman_runs_x': 'batsman_runs_x',
    'total_runs_x': 'total_runs_x',
    'total_runs_y': 'total_runs_y',
    'batsman_runs_y': 'batsman_runs_y',
    'batsman_runs': 'batsman_runs'
})

final['total_runs_x'] = final['total_runs_x'].fillna(0).astype('Int64')
final['total_runs_y'] = final['total_runs_y'].fillna(0).astype('Int64')
final['batsman_runs_x'] = final['batsman_runs_x'].astype(float)
final['batsman_runs_y'] = final['batsman_runs_y'].astype(float)
final['batsman_runs'] = final['batsman_runs'].fillna(0).astype(int)

final = final[['batsman', 'batsman_runs_x', 'total_runs_x', 'total_runs_y', 'batsman_runs_y', 'batsman_runs']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_33/target_multisource_mcts.csv", index=False)