import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_56/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_56/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_56/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_56/training_3.csv", index_col=0)

# Rename columns in each source to distinguish them after join
df0_renamed = df0.rename(columns={
    'CountyID': 'CountyID_x',
    'CountyName': 'CountyName_x',
    'whites_population': 'whites_population',
    'Year': 'Year_x',
    'ID': 'ID'
})

df1_renamed = df1.rename(columns={
    'CountyID': 'CountyID_y_13',
    'CountyName': 'CountyName_y_14',
    'asian_population': 'asian_population',
    'Year': 'Year_y_16',
    'ID': 'ID_y'
})

df2_renamed = df2.rename(columns={
    'CountyID': 'CountyID_y',
    'CountyName': 'CountyName_y',
    'other_population': 'other_population',
    'Year': 'Year_y',
    'ID': 'ID_y2'
})

df3_renamed = df3.rename(columns={
    'CountyID': 'CountyID_x_9',
    'CountyName': 'CountyName_x_10',
    'mixed_population': 'mixed_population',
    'Year': 'Year_x_12',
    'ID': 'ID_x2'
})

# Start joining on CountyID keys
# Join df0 and df2 on CountyID_x == CountyID_y
join_1 = pd.merge(df0_renamed, df2_renamed, left_on='CountyID_x', right_on='CountyID_y', how='inner')

# Join join_1 and df3 on CountyID_x == CountyID_x_9
join_2 = pd.merge(join_1, df3_renamed, left_on='CountyID_x', right_on='CountyID_x_9', how='inner')

# Join join_2 and df1 on CountyID_x == CountyID_y_13
final_df = pd.merge(join_2, df1_renamed, left_on='CountyID_x', right_on='CountyID_y_13', how='inner')

# Select and reorder columns to match target schema exactly
final_df = final_df[[
    'CountyID_x', 'CountyName_x', 'whites_population', 'Year_x', 'ID',
    'CountyID_y', 'CountyName_y', 'other_population', 'Year_y',
    'CountyID_x_9', 'CountyName_x_10', 'mixed_population', 'Year_x_12',
    'CountyID_y_13', 'CountyName_y_14', 'asian_population', 'Year_y_16'
]]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length3_56/target_multisource_mcts.csv")