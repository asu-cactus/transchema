import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_56/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_56/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_56/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_56/training_3.csv", index_col=0)

join_0 = pd.merge(df0, df2, how='inner', left_on=['CountyID', 'Year'], right_on=['CountyID', 'Year'], suffixes=('_x', '_y'))
join_1 = pd.merge(join_0, df3, how='inner', left_on=['CountyID', 'Year'], right_on=['CountyID', 'Year'], suffixes=('', '_z'))
final_join = pd.merge(join_1, df1, how='inner', left_on=['CountyID', 'Year'], right_on=['CountyID', 'Year'], suffixes=('', '_w'))

result = pd.DataFrame()
result['CountyID_x'] = final_join['CountyID']
result['CountyName_x'] = final_join['CountyName_x']
result['whites_population'] = final_join['whites_population']
result['Year_x'] = final_join['Year']
result['ID'] = final_join['ID']
result['CountyID_y'] = final_join['CountyID']
result['CountyName_y'] = final_join['CountyName_y']
result['other_population'] = final_join['other_population']
result['Year_y'] = final_join['Year']
result['CountyID_x_9'] = final_join['CountyID']
result['CountyName_x_10'] = final_join['CountyName']
result['mixed_population'] = final_join['mixed_population']
result['Year_x_12'] = final_join['Year']
result['CountyID_y_13'] = final_join['CountyID']
result['CountyName_y_14'] = final_join['CountyName']
result['asian_population'] = final_join['asian_population']
result['Year_y_16'] = final_join['Year']

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_56/target_multisource_mcts.csv", index=False)