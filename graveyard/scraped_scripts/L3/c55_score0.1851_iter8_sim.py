import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_55/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_55/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_55/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_55/training_3.csv", index_col=0)

df0_renamed = df0.rename(columns={
    'CountyID': 'CountyID_x',
    'CountyName': 'CountyName_x',
    'whites_population': 'whites_population',
    'Year': 'Year_x',
    'ID': 'ID'
})[['CountyID_x', 'CountyName_x', 'whites_population', 'Year_x', 'ID']]

df1_renamed = df1.rename(columns={
    'CountyID': 'CountyID_y',
    'CountyName': 'CountyName_y',
    'other_population': 'other_population',
    'Year': 'Year_y',
    'ID': 'ID'
})[['CountyID_y', 'CountyName_y', 'other_population', 'Year_y', 'ID']]

df2_renamed = df2.rename(columns={
    'CountyID': 'CountyID_x_9',
    'CountyName': 'CountyName_x_10',
    'mixed_population': 'mixed_population',
    'Year': 'Year_x_12',
    'ID': 'ID'
})[['CountyID_x_9', 'CountyName_x_10', 'mixed_population', 'Year_x_12', 'ID']]

df3_renamed = df3.rename(columns={
    'CountyID': 'CountyID_y_13',
    'CountyName': 'CountyName_y_14',
    'aian_population': 'aian_population',
    'Year': 'Year_y_16',
    'ID': 'ID'
})[['CountyID_y_13', 'CountyName_y_14', 'aian_population', 'Year_y_16', 'ID']]

df_merged = df0_renamed.merge(df1_renamed, on='ID', how='outer')
df_merged = df_merged.merge(df2_renamed, on='ID', how='outer')
df_merged = df_merged.merge(df3_renamed, on='ID', how='outer')

df_merged = df_merged[['CountyID_x', 'CountyName_x', 'whites_population', 'Year_x', 'ID',
                       'CountyID_y', 'CountyName_y', 'other_population', 'Year_y',
                       'CountyID_x_9', 'CountyName_x_10', 'mixed_population', 'Year_x_12',
                       'CountyID_y_13', 'CountyName_y_14', 'aian_population', 'Year_y_16']]

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length3_55/target_multisource_mcts.csv", index=False)