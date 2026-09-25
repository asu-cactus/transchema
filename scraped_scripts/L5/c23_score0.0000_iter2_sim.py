import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_23/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_23/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_23/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_23/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_23/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_23/training_5.csv", index_col=0)

join0 = pd.merge(df0, df4, on=["CountyID", "Year"], suffixes=('_x', '_y'))
join1 = pd.merge(join0, df1, on=["CountyID", "Year"], suffixes=('', '_1'))
join2 = pd.merge(join1, df5, on=["CountyID", "Year"], suffixes=('', '_5'))
join3 = pd.merge(join2, df3, on=["CountyID", "Year"], suffixes=('', '_3'))
join4 = pd.merge(join3, df2, on=["CountyID", "Year"], suffixes=('', '_2'))

# Rename columns to match target schema with suffixes and multiple CountyID/CountyName columns
result = pd.DataFrame()

result['CountyID_x'] = join4['CountyID']
result['CountyName_x'] = join4['CountyName']
result['whites_population'] = join4['whites_population']
result['Year_x'] = join4['Year']
result['ID'] = join4['ID']

result['CountyID_y'] = join4['CountyID_y']
result['CountyName_y'] = join4['CountyName_y']
result['other_population'] = join4['other_population']
result['Year_y'] = join4['Year_y']

result['CountyID_x_9'] = join4['CountyID_1']
result['CountyName_x_10'] = join4['CountyName_1']
result['mixed_population'] = join4['mixed_population']
result['Year_x_12'] = join4['Year_1']

result['CountyID_y_13'] = join4['CountyID_5']
result['CountyName_y_14'] = join4['CountyName_5']
result['hispanic_population'] = join4['hispanic_population']
result['Year_y_16'] = join4['Year_5']

result['CountyID_x_17'] = join4['CountyID_3']
result['CountyName_x_18'] = join4['CountyName_3']
result['black_population'] = join4['black_population']
result['Year_x_20'] = join4['Year_3']

result['CountyID_y_21'] = join4['CountyID_2']
result['CountyName_y_22'] = join4['CountyName_2']
result['aian_population'] = join4['aian_population']
result['Year_y_24'] = join4['Year_2']

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_23/target_multisource_mcts.csv", index=False)