import pandas as pd

# Read source tables with index_col=0 to ignore the first column
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_4.csv", index_col=0)

# Join batsman_runs tables: s0, s3, s4
# Use suffixes to distinguish columns
join_batsman_runs_0_3 = pd.merge(s0, s3, on="batsman", how="inner", suffixes=('_x', '_y'))
join_batsman_runs_all = pd.merge(join_batsman_runs_0_3, s4, on="batsman", how="inner")

# Rename columns to match target schema
# s0.batsman_runs -> batsman_runs_x (already _x)
# s3.batsman_runs -> batsman_runs_y (already _y)
# s4.batsman_runs -> batsman_runs (no suffix)

# Join total_runs tables: s1, s2
join_total_runs = pd.merge(s1, s2, on="batsman", how="inner", suffixes=('_x', '_y'))

# Now join the two big tables on batsman
final_join = pd.merge(join_batsman_runs_all, join_total_runs, on="batsman", how="inner")

# Reorder columns to match target schema:
# ['batsman', 'batsman_runs_x', 'total_runs_x', 'total_runs_y', 'batsman_runs_y', 'batsman_runs']

result = final_join[['batsman', 'batsman_runs_x', 'total_runs_x', 'total_runs_y', 'batsman_runs_y', 'batsman_runs']]

# Ensure correct dtypes:
result['batsman_runs_x'] = result['batsman_runs_x'].astype(float)
result['total_runs_x'] = result['total_runs_x'].astype(int)
result['total_runs_y'] = result['total_runs_y'].astype(int)
result['batsman_runs_y'] = result['batsman_runs_y'].astype(int)
result['batsman_runs'] = result['batsman_runs'].astype(int)

# Write to CSV without the index
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_33/target_multisource_mcts.csv", index=False)