import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_4.csv", index_col=0)

# Join Source0 and Source3 on 'batsman' to get batsman_runs_x and batsman_runs_y
join_03 = pd.merge(df0, df3, on="batsman", how="inner", suffixes=('_x', '_y'))

# Join Source1 and Source4 on 'batsman' to get total_runs_x and total_runs_y
join_14 = pd.merge(df1, df4, on="batsman", how="inner", suffixes=('_x', '_y'))

# Join the above two results on 'batsman'
join_0314 = pd.merge(join_03, join_14, on="batsman", how="inner")

# Finally join with Source2 on 'batsman'
final_join = pd.merge(join_0314, df2, on="batsman", how="inner")

# Rename columns to match target schema exactly
final = final_join.rename(columns={
    'total_runs_x': 'total_runs_x',
    'batsman_runs_x': 'batsman_runs_x',
    'batsman_runs_y': 'batsman_runs_y',
    'no of balls': 'no of balls',
    'batsman_runs': 'batsman_runs',
    'strike': 'strike',
    'total_runs_y': 'total_runs_y'
})[['batsman', 'total_runs_x', 'batsman_runs_x', 'batsman_runs_y', 'no of balls', 'batsman_runs', 'strike', 'total_runs_y']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_34/target_multisource_mcts.csv", index=False)