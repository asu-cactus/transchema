import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_4.csv", index_col=0)

join_0 = pd.merge(s0, s1, on="batsman", how="inner")
join_1 = pd.merge(join_0, s2, on="batsman", how="inner", suffixes=('_x', '_y'))
join_2 = pd.merge(join_1, s3, on="batsman", how="inner", suffixes=('', '_y'))
join_3 = pd.merge(join_2, s4, on="batsman", how="inner", suffixes=('_x', ''))

# After merges, columns:
# batsman, batsman_runs_x (from s0), total_runs_x (from s1), total_runs_y (from s2),
# batsman_runs_y (from s3), batsman_runs (from s4)

# Ensure correct dtypes:
join_3['batsman_runs_x'] = join_3['batsman_runs_x'].astype(float)
join_3['total_runs_x'] = join_3['total_runs_x'].astype(int)
join_3['total_runs_y'] = join_3['total_runs_y'].astype(int)
join_3['batsman_runs_y'] = join_3['batsman_runs_y'].astype(int)
join_3['batsman_runs'] = join_3['batsman_runs'].astype(int)

result = join_3[['batsman', 'batsman_runs_x', 'total_runs_x', 'total_runs_y', 'batsman_runs_y', 'batsman_runs']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_33/target_multisource_mcts.csv")