import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_55/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_55/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_55/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_55/training_3.csv", index_col=0)

join_0 = pd.merge(df0, df1, how='inner', on=['CountyID', 'CountyName', 'Year', 'ID'])
join_1 = pd.merge(join_0, df2, how='inner', on=['CountyID', 'CountyName', 'Year', 'ID'])
join_2 = pd.merge(join_1, df3, how='inner', on=['CountyID', 'CountyName', 'Year', 'ID'])

result = pd.DataFrame()
result['CountyID_x'] = join_2['CountyID']
result['CountyName_x'] = join_2['CountyName']
result['whites_population'] = join_2['whites_population']
result['Year_x'] = join_2['Year']
result['ID'] = join_2['ID']

result['CountyID_y'] = join_2['CountyID']
result['CountyName_y'] = join_2['CountyName']
result['other_population'] = join_2['other_population']
result['Year_y'] = join_2['Year']

result['CountyID_x_9'] = join_2['CountyID']
result['CountyName_x_10'] = join_2['CountyName']
result['mixed_population'] = join_2['mixed_population']
result['Year_x_12'] = join_2['Year']

result['CountyID_y_13'] = join_2['CountyID']
result['CountyName_y_14'] = join_2['CountyName']
result['aian_population'] = join_2['aian_population']
result['Year_y_16'] = join_2['Year']

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_55/target_multisource_mcts.csv", index=False)