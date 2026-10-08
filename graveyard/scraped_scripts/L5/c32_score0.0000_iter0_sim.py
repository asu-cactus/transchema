import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_32/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_32/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_32/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_32/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_32/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_32/training_5.csv", index_col=0)

j0 = pd.merge(s3, s5, how='inner', on=['CountyID', 'Year'], suffixes=('_x', '_y'))
j1 = pd.merge(j0, s4, how='inner', left_on=['CountyID_x', 'Year_x'], right_on=['CountyID', 'Year'], suffixes=('', '_9'))
j1 = j1.rename(columns={
    'CountyID': 'CountyID_x_9',
    'CountyName': 'CountyName_x_10',
    'Year': 'Year_x_12',
    'mixed_population': 'mixed_population',
})
j1 = j1.drop(columns=['ID', 'ID_9'], errors='ignore')

j2 = pd.merge(j1, s2, how='inner', left_on=['CountyID_x', 'Year_x'], right_on=['CountyID', 'Year'], suffixes=('', '_13'))
j2 = j2.rename(columns={
    'CountyID': 'CountyID_y_13',
    'CountyName': 'CountyName_y_14',
    'black_population': 'black_population',
    'Year': 'Year_y_16',
})
j2 = j2.drop(columns=['ID', 'ID_13'], errors='ignore')

j3 = pd.merge(j2, s0, how='inner', left_on=['CountyID_x', 'Year_x'], right_on=['CountyID', 'Year'], suffixes=('', '_17'))
j3 = j3.rename(columns={
    'CountyID': 'CountyID_x_17',
    'CountyName': 'CountyName_x_18',
    'asian_population': 'asian_population',
    'Year': 'Year_x_20',
})
j3 = j3.drop(columns=['ID', 'ID_17'], errors='ignore')

j4 = pd.merge(j3, s1, how='inner', left_on=['CountyID_x', 'Year_x'], right_on=['CountyID', 'Year'], suffixes=('', '_21'))
j4 = j4.rename(columns={
    'CountyID': 'CountyID_y_21',
    'CountyName': 'CountyName_y_22',
    'aian_population': 'aian_population',
    'Year': 'Year_y_24',
})
j4 = j4.drop(columns=['ID', 'ID_21'], errors='ignore')

j4.to_csv("autopipeline-benchmarks/github-pipelines/length5_32/target_multisource_mcts.csv", index=False)