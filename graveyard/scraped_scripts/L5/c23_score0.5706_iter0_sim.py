import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_23/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_23/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_23/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_23/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_23/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_23/training_5.csv", index_col=0)

r0 = pd.merge(df0, df4, on=['CountyID', 'CountyName', 'Year', 'ID'], how='inner', suffixes=('_x', '_y'))
r1 = pd.merge(r0, df1, on=['CountyID', 'CountyName', 'Year', 'ID'], how='inner', suffixes=('', '_1'))
r2 = pd.merge(r1, df5, on=['CountyID', 'CountyName', 'Year', 'ID'], how='inner', suffixes=('', '_5'))
r3 = pd.merge(r2, df2, on=['CountyID', 'CountyName', 'Year', 'ID'], how='inner', suffixes=('', '_2'))
r4 = pd.merge(r3, df3, on=['CountyID', 'CountyName', 'Year', 'ID'], how='inner', suffixes=('', '_3'))

out = pd.DataFrame()
out['CountyID_x'] = r4['CountyID']
out['CountyName_x'] = r4['CountyName']
out['whites_population'] = r4['whites_population']
out['Year_x'] = r4['Year']
out['ID'] = r4['ID']
out['CountyID_y'] = r4['CountyID']
out['CountyName_y'] = r4['CountyName']
out['other_population'] = r4['other_population']
out['Year_y'] = r4['Year']
out['CountyID_x_9'] = r4['CountyID']
out['CountyName_x_10'] = r4['CountyName']
out['mixed_population'] = r4['mixed_population']
out['Year_x_12'] = r4['Year']
out['CountyID_y_13'] = r4['CountyID']
out['CountyName_y_14'] = r4['CountyName']
out['hispanic_population'] = r4['hispanic_population']
out['Year_y_16'] = r4['Year']
out['CountyID_x_17'] = r4['CountyID']
out['CountyName_x_18'] = r4['CountyName']
out['black_population'] = r4['black_population']
out['Year_x_20'] = r4['Year']
out['CountyID_y_21'] = r4['CountyID']
out['CountyName_y_22'] = r4['CountyName']
out['aian_population'] = r4['aian_population']
out['Year_y_24'] = r4['Year']

out.to_csv("autopipeline-benchmarks/github-pipelines/length5_23/target_multisource_mcts.csv", index=False)