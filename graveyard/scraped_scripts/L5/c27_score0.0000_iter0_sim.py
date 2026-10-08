import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_27/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_27/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_27/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_27/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_27/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_27/training_5.csv", index_col=0)

join_0 = pd.merge(s4, s2, how='inner', on=['CountyID', 'Year'], suffixes=('_x', '_y'))
join_1 = pd.merge(join_0, s1, how='inner', left_on=['CountyID_x', 'Year_x'], right_on=['CountyID', 'Year'], suffixes=('', '_y'))
join_2 = pd.merge(join_1, s0, how='inner', left_on=['CountyID_x', 'Year_x'], right_on=['CountyID', 'Year'], suffixes=('', '_y'))
join_3 = pd.merge(join_2, s3, how='inner', left_on=['CountyID_x', 'Year_x'], right_on=['CountyID', 'Year'], suffixes=('', '_y'))
join_4 = pd.merge(join_3, s5, how='inner', left_on=['CountyID_x', 'Year_x'], right_on=['CountyID', 'Year'], suffixes=('', '_y'))

result = join_4.rename(columns={
    'CountyID_x': 'CountyID_x',
    'CountyName_x': 'CountyName_x',
    'whites_population': 'whites_population',
    'Year_x': 'Year_x',
    'ID': 'ID',
    'CountyID_y': 'CountyID_y',
    'CountyName_y': 'CountyName_y',
    'other_population': 'other_population',
    'Year_y': 'Year_y',
    'CountyID': 'CountyID_x_9',
    'CountyName': 'CountyName_x_10',
    'mixed_population': 'mixed_population',
    'Year': 'Year_x_12',
    'CountyID_y_y': 'CountyID_y_13',
    'CountyName_y_y': 'CountyName_y_14',
    'hispanic_population': 'hispanic_population',
    'Year_y_y': 'Year_y_16',
    'CountyID_y': 'CountyID_x_17',
    'CountyName_y': 'CountyName_x_18',
    'asian_population': 'asian_population',
    'Year': 'Year_x_20',
    'CountyID_y_y_y': 'CountyID_y_21',
    'CountyName_y_y_y': 'CountyName_y_22',
    'aian_population': 'aian_population',
    'Year_y_y_y': 'Year_y_24'
}, errors='ignore')

cols = [
    'CountyID_x', 'CountyName_x', 'whites_population', 'Year_x', 'ID',
    'CountyID_y', 'CountyName_y', 'other_population', 'Year_y',
    'CountyID_x_9', 'CountyName_x_10', 'mixed_population', 'Year_x_12',
    'CountyID_y_13', 'CountyName_y_14', 'hispanic_population', 'Year_y_16',
    'CountyID_x_17', 'CountyName_x_18', 'asian_population', 'Year_x_20',
    'CountyID_y_21', 'CountyName_y_22', 'aian_population', 'Year_y_24'
]

result = result[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_27/target_multisource_mcts.csv")