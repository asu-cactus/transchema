import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_38/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_38/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_38/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_38/training_3.csv", index_col=0)

j1 = pd.merge(s1, s3, on="batsman", how="inner", suffixes=('_x', '_y'))
j2 = pd.merge(j1, s0, on="batsman", how="inner")
j3 = pd.merge(j2, s2, on="batsman", how="inner", suffixes=('', '_z'))

result = j3.rename(columns={
    'total_runs_x': 'total_runs',
    'batsman_runs_x': 'batsman_runs_x',
    'batsman_runs_y': 'batsman_runs_y',
    'batsman_runs': 'batsman_runs'
})

result = result[['batsman', 'batsman_runs_x', 'total_runs', 'batsman_runs_y', 'batsman_runs']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_38/target_multisource_mcts.csv", index=False)