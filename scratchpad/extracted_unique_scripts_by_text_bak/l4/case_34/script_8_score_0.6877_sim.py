import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_4.csv", index_col=0)

join01 = pd.merge(df0, df1, on="batsman", how="inner", suffixes=('_x', '_y'))
join013 = pd.merge(join01, df3, on="batsman", how="inner", suffixes=('_x', '_y'))
join0134 = pd.merge(join013, df4, on="batsman", how="inner", suffixes=('_x', '_y'))
final_join = pd.merge(join0134, df2, on="batsman", how="inner")

final = final_join.rename(columns={
    'batsman_runs_x': 'batsman_runs_x',
    'batsman_runs_y': 'batsman_runs_y',
    'total_runs_x': 'total_runs_x',
    'total_runs_y': 'total_runs_y',
    'no of balls': 'no of balls',
    'batsman_runs': 'batsman_runs',
    'strike': 'strike'
})[['batsman', 'total_runs_x', 'batsman_runs_x', 'batsman_runs_y', 'no of balls', 'batsman_runs', 'strike', 'total_runs_y']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_34/target_multisource_mcts.csv", index=False)