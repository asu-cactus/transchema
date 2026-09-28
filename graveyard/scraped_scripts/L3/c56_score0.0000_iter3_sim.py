import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_56/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_56/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_56/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_56/training_3.csv", index_col=0)

join_0 = pd.merge(df0, df2, how='inner', on=['CountyID', 'Year'], suffixes=('_x', '_y'))
join_1 = pd.merge(join_0, df3, how='inner', on=['CountyID', 'Year'], suffixes=('', '_y'))
join_1 = join_1.rename(columns={
    'CountyName': 'CountyName_x_10',
    'mixed_population': 'mixed_population',
    'Year': 'Year_x_12',
    'ID': 'ID_x_12'
})
join_1 = join_1.drop(columns=['CountyName_y', 'ID_y'], errors='ignore')

final = pd.merge(join_1, df1, how='inner', on=['CountyID', 'Year'], suffixes=('_x', '_y'))

final = final.rename(columns={
    'CountyID': 'CountyID_x',
    'CountyName_x': 'CountyName_x',
    'whites_population': 'whites_population',
    'Year_x': 'Year_x',
    'ID_x': 'ID',
    'CountyID_y': 'CountyID_y',
    'CountyName_y': 'CountyName_y',
    'other_population': 'other_population',
    'Year_y': 'Year_y',
    'CountyID_x_9': 'CountyID_x_9',
    'CountyName_x_10': 'CountyName_x_10',
    'mixed_population': 'mixed_population',
    'Year_x_12': 'Year_x_12',
    'CountyID_y_13': 'CountyID_y_13',
    'CountyName_y_14': 'CountyName_y_14',
    'asian_population': 'asian_population',
    'Year_y_16': 'Year_y_16'
})

# The join_1 columns for CountyID_x_9, CountyName_x_10, Year_x_12, CountyID_y_13, CountyName_y_14, Year_y_16
# are not yet set correctly. We need to create these columns from the appropriate columns.

# From join_1 (which is df0+df2+df3 merged), we have:
# CountyID_x_9 = CountyID (same as CountyID_x)
# CountyName_x_10 = CountyName_x (from df0)
# Year_x_12 = Year_x (from df0)
# CountyID_y_13 = CountyID (same as CountyID_y from df1)
# CountyName_y_14 = CountyName_y (from df1)
# Year_y_16 = Year_y (from df1)

# So we assign these columns accordingly:

final['CountyID_x_9'] = final['CountyID_x']
final['CountyName_x_10'] = final['CountyName_x']
final['Year_x_12'] = final['Year_x']
final['CountyID_y_13'] = final['CountyID_y']
final['CountyName_y_14'] = final['CountyName_y']
final['Year_y_16'] = final['Year_y']

final = final[['CountyID_x', 'CountyName_x', 'whites_population', 'Year_x', 'ID',
               'CountyID_y', 'CountyName_y', 'other_population', 'Year_y',
               'CountyID_x_9', 'CountyName_x_10', 'mixed_population', 'Year_x_12',
               'CountyID_y_13', 'CountyName_y_14', 'asian_population', 'Year_y_16']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_56/target_multisource_mcts.csv", index=False)