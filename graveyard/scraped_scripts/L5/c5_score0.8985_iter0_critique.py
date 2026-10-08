import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_5/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_5/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_5/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_5/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_5/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_5/training_5.csv", index_col=0)

# Rename key columns in each source to unique names to avoid suffixes during merge
s4_renamed = s4.rename(columns={
    'CountyID': 'CountyID_x',
    'CountyName': 'CountyName_x',
    'Year': 'Year_x',
    'ID': 'ID'
})

s2_renamed = s2.rename(columns={
    'CountyID': 'CountyID_y',
    'CountyName': 'CountyName_y',
    'Year': 'Year_y',
    'ID': 'ID_y'
})

s0_renamed = s0.rename(columns={
    'CountyID': 'CountyID_x_9',
    'CountyName': 'CountyName_x_10',
    'Year': 'Year_x_12',
    'ID': 'ID_x_12'  # ID not in target schema except once, keep for completeness
})

s1_renamed = s1.rename(columns={
    'CountyID': 'CountyID_y_13',
    'CountyName': 'CountyName_y_14',
    'Year': 'Year_y_16',
    'ID': 'ID_y_16'
})

s5_renamed = s5.rename(columns={
    'CountyID': 'CountyID_x_17',
    'CountyName': 'CountyName_x_18',
    'Year': 'Year_x_20',
    'ID': 'ID_x_20'
})

s3_renamed = s3.rename(columns={
    'CountyID': 'CountyID_y_21',
    'CountyName': 'CountyName_y_22',
    'Year': 'Year_y_24',
    'ID': 'ID_y_24'
})

# Merge s4 and s2 on CountyID and Year (original keys)
j0 = pd.merge(
    s4_renamed, s2_renamed,
    left_on=['CountyID_x', 'Year_x'],
    right_on=['CountyID_y', 'Year_y'],
    how='inner'
)

# Merge with s0
j1 = pd.merge(
    j0, s0_renamed,
    left_on=['CountyID_x', 'Year_x'],
    right_on=['CountyID_x_9', 'Year_x_12'],
    how='inner'
)

# Merge with s1
j2 = pd.merge(
    j1, s1_renamed,
    left_on=['CountyID_x', 'Year_x'],
    right_on=['CountyID_y_13', 'Year_y_16'],
    how='inner'
)

# Merge with s5
j3 = pd.merge(
    j2, s5_renamed,
    left_on=['CountyID_x', 'Year_x'],
    right_on=['CountyID_x_17', 'Year_x_20'],
    how='inner'
)

# Merge with s3
j4 = pd.merge(
    j3, s3_renamed,
    left_on=['CountyID_x', 'Year_x'],
    right_on=['CountyID_y_21', 'Year_y_24'],
    how='inner'
)

# Select and reorder columns exactly as in target schema
result = j4[[
    'CountyID_x', 'CountyName_x', 'whites_population', 'Year_x', 'ID',
    'CountyID_y', 'CountyName_y', 'other_population', 'Year_y',
    'CountyID_x_9', 'CountyName_x_10', 'mixed_population', 'Year_x_12',
    'CountyID_y_13', 'CountyName_y_14', 'hispanic_population', 'Year_y_16',
    'CountyID_x_17', 'CountyName_x_18', 'black_population', 'Year_x_20',
    'CountyID_y_21', 'CountyName_y_22', 'asian_population', 'Year_y_24'
]]

# Write to CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_5/target_multisource_mcts.csv", index=False)