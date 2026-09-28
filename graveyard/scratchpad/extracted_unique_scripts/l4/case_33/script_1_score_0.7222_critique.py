import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_33/training_4.csv", index_col=0)

# Join total_runs tables: s1 and s2
join_01 = pd.merge(s1, s2, on="batsman", how="inner", suffixes=('_x', '_y'))

# Join batsman_runs integer tables: s0 and s3
join_02 = pd.merge(s0, s3, on="batsman", how="inner", suffixes=('_y', ''))  # suffix '' to avoid double suffix on s3

# Rename columns in join_02 to match target schema
join_02 = join_02.rename(columns={
    'batsman_runs_y': 'batsman_runs_y',
    'batsman_runs': 'batsman_runs'
})

# Join the above two results with s4 (float batsman_runs)
final = pd.merge(join_01, join_02, on="batsman", how="inner")
final = pd.merge(final, s4, on="batsman", how="inner")

# Rename columns to match target schema exactly
final = final.rename(columns={
    'batsman_runs': 'batsman_runs_x',  # from s4
    'batsman_runs_y': 'batsman_runs_y',
    'batsman_runs_y_y': 'batsman_runs',  # from s3 (after merge suffix)
    'total_runs_x': 'total_runs_x',
    'total_runs_y': 'total_runs_y'
})

# After merges, columns may have suffixes; fix them explicitly:
# The columns after merges are:
# batsman
# total_runs_x (from s1)
# total_runs_y (from s2)
# batsman_runs_y (from s0)
# batsman_runs (from s3)
# batsman_runs (from s4) → renamed to batsman_runs_x

# But because of suffixes, let's check and rename carefully:

# The join_01 columns: batsman, total_runs_x, total_runs_y
# The join_02 columns: batsman, batsman_runs_y, batsman_runs
# s4 columns: batsman, batsman_runs (float)

# After merging join_01 and join_02, columns:
# batsman, total_runs_x, total_runs_y, batsman_runs_y, batsman_runs

# After merging with s4, batsman_runs column from s4 will be added, but since s4 has 'batsman_runs' column, pandas will add suffix '_x' or '_y'

# To avoid confusion, rename s4 column before merge:

s4 = s4.rename(columns={'batsman_runs': 'batsman_runs_x'})

final = pd.merge(join_01, join_02, on="batsman", how="inner")
final = pd.merge(final, s4, on="batsman", how="inner")

# Select and reorder columns as per target schema
final = final[['batsman', 'batsman_runs_x', 'total_runs_x', 'total_runs_y', 'batsman_runs_y', 'batsman_runs']]

# Cast types as per target schema
final['batsman_runs_x'] = final['batsman_runs_x'].astype(float)
final['total_runs_x'] = final['total_runs_x'].astype(int)
final['total_runs_y'] = final['total_runs_y'].astype(int)
final['batsman_runs_y'] = final['batsman_runs_y'].astype(int)
final['batsman_runs'] = final['batsman_runs'].astype(int)

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_33/target_multisource_mcts.csv", index=False)