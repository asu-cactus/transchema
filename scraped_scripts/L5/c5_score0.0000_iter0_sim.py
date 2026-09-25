import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_5/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_5/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_5/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_5/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_5/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_5/training_5.csv", index_col=0)

j0 = pd.merge(s4, s2, how='inner', left_on=['CountyID', 'Year'], right_on=['CountyID', 'Year'], suffixes=('_x', '_y'))
j1 = pd.merge(j0, s0, how='inner', left_on=['CountyID_x', 'Year_x'], right_on=['CountyID', 'Year'], suffixes=('', '_z'))
j2 = pd.merge(j1, s1, how='inner', left_on=['CountyID_x', 'Year_x'], right_on=['CountyID', 'Year'], suffixes=('', '_a'))
j3 = pd.merge(j2, s5, how='inner', left_on=['CountyID_x', 'Year_x'], right_on=['CountyID', 'Year'], suffixes=('', '_b'))
j4 = pd.merge(j3, s3, how='inner', left_on=['CountyID_x', 'Year_x'], right_on=['CountyID', 'Year'], suffixes=('', '_c'))

result = pd.DataFrame()
result['CountyID_x'] = j4['CountyID_x']
result['CountyName_x'] = j4['CountyName_x']
result['whites_population'] = j4['whites_population']
result['Year_x'] = j4['Year_x']
result['ID'] = j4['ID']
result['CountyID_y'] = j4['CountyID_y']
result['CountyName_y'] = j4['CountyName_y']
result['other_population'] = j4['other_population']
result['Year_y'] = j4['Year_y']
result['CountyID_x_9'] = j4['CountyID']
result['CountyName_x_10'] = j4['CountyName']
result['mixed_population'] = j4['mixed_population']
result['Year_x_12'] = j4['Year']
result['CountyID_y_13'] = j4['CountyID_a']
result['CountyName_y_14'] = j4['CountyName_a']
result['hispanic_population'] = j4['hispanic_population']
result['Year_y_16'] = j4['Year_a']
result['CountyID_x_17'] = j4['CountyID_b']
result['CountyName_x_18'] = j4['CountyName_b']
result['black_population'] = j4['black_population']
result['Year_x_20'] = j4['Year_b']
result['CountyID_y_21'] = j4['CountyID_c']
result['CountyName_y_22'] = j4['CountyName_c']
result['asian_population'] = j4['asian_population']
result['Year_y_24'] = j4['Year_c']

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_5/target_multisource_mcts.csv", index=False)