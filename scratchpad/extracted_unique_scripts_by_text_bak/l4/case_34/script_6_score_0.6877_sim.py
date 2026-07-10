import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_4.csv", index_col=0)

j1 = pd.merge(s2, s4, on="batsman", how="inner", suffixes=('_x', '_y'))
j2 = pd.merge(j1, s0, on="batsman", how="inner")
j3 = pd.merge(j2, s1, on="batsman", how="inner", suffixes=('_x', '_y'))
j4 = pd.merge(j3, s3, on="batsman", how="inner", suffixes=('_y', ''))

# Rename columns to match target schema exactly
# j4 columns: batsman, no of balls, batsman_runs_x, strike, total_runs_y, batsman_runs, total_runs_x, batsman_runs (from s3)
# After merges, columns from s0 and s3 both named batsman_runs, suffixes applied only on last merge for s3
# We have batsman_runs_x (from s0), batsman_runs_y (from s3) after last merge, but suffixes used only on last merge
# Actually, last merge suffixes=('_y','') means s3 batsman_runs has no suffix, s1 batsman_runs has _y suffix
# But s1 has total_runs only, no batsman_runs, so suffixes on last merge only affect total_runs columns? No, s1 has total_runs only.
# So after last merge, batsman_runs from s3 remains as 'batsman_runs', batsman_runs from s0 is 'batsman_runs_x' (from previous merge)
# total_runs_x from s1, total_runs_y from s4

# Let's rename columns explicitly to target schema:
# target schema: ['batsman', 'total_runs_x', 'batsman_runs_x', 'batsman_runs_y', 'no of balls', 'batsman_runs', 'strike', 'total_runs_y']

# j4 columns:
# batsman
# no of balls
# batsman_runs_x (from s0)
# strike
# total_runs_y (from s4)
# batsman_runs (from s3)
# total_runs_x (from s1)
# batsman_runs_y (from s2) - but s2 batsman_runs is renamed to batsman_runs_x in first merge? No, s2 batsman_runs is original, s4 total_runs is total_runs_y

# Actually, after first merge:
# s2 columns: batsman, no of balls, batsman_runs, strike
# s4 columns: batsman, total_runs
# merge suffixes=('_x','_y') => batsman_runs_x (from s2), total_runs_y (from s4)
# Then merge with s0 (batsman, batsman_runs) no suffixes => batsman_runs (from s0)
# Then merge with s1 (batsman, total_runs) suffixes=('_x','_y') => total_runs_x (from previous), total_runs_y (from s1)
# But s1 has total_runs only, no batsman_runs, so suffixes apply to total_runs columns
# Then merge with s3 (batsman, batsman_runs) suffixes=('_y','') => batsman_runs_y (from s3), batsman_runs_x (from previous)
# But s3 batsman_runs has no suffix, s3 batsman_runs is 'batsman_runs' after merge, previous batsman_runs is 'batsman_runs_y'?

# To avoid confusion, let's rename columns explicitly after all merges.

df = j4.rename(columns={
    'total_runs_x': 'total_runs_x',
    'batsman_runs_x': 'batsman_runs_x',
    'batsman_runs_y': 'batsman_runs_y',
    'no of balls': 'no of balls',
    'batsman_runs': 'batsman_runs',
    'strike': 'strike',
    'total_runs_y': 'total_runs_y'
})

df = df[['batsman', 'total_runs_x', 'batsman_runs_x', 'batsman_runs_y', 'no of balls', 'batsman_runs', 'strike', 'total_runs_y']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_34/target_multisource_mcts.csv", index=False)