import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_27/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_27/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_27/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_27/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_27/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_27/training_5.csv", index_col=0)

j0 = pd.merge(s4, s2, how='inner', on=['CountyID', 'Year'], suffixes=('_x', '_y'))
j1 = pd.merge(j0, s1, how='inner', on=['CountyID', 'Year'], suffixes=('', '_y'))
j1 = j1.rename(columns={
    'CountyName': 'CountyName_x',
    'CountyName_y': 'CountyName_y',
    'mixed_population': 'mixed_population',
    'ID_y': 'ID_y'
})
# After merge, columns from s1 that conflict with j0's CountyName_x and CountyName_y are renamed:
# But s1 has CountyName, so to avoid conflicts, rename s1's CountyName to CountyName_y_10 temporarily
# Instead, to avoid confusion, rename s1's CountyName before merge:
s1_renamed = s1.rename(columns={'CountyName': 'CountyName_y_10'})
j1 = pd.merge(j0, s1_renamed, how='inner', on=['CountyID', 'Year'], suffixes=('', '_y'))

j2 = pd.merge(j1, s0.rename(columns={'CountyName': 'CountyName_y_14'}), how='inner', on=['CountyID', 'Year'], suffixes=('', '_y'))
j3 = pd.merge(j2, s3.rename(columns={'CountyName': 'CountyName_x_18'}), how='inner', on=['CountyID', 'Year'], suffixes=('', '_y'))
j4 = pd.merge(j3, s5.rename(columns={'CountyName': 'CountyName_y_22'}), how='inner', on=['CountyID', 'Year'], suffixes=('', '_y'))

# Now rename columns to match target schema exactly:
# Target columns:
# ['CountyID_x', 'CountyName_x', 'whites_population', 'Year_x', 'ID',
#  'CountyID_y', 'CountyName_y', 'other_population', 'Year_y',
#  'CountyID_x_9', 'CountyName_x_10', 'mixed_population', 'Year_x_12',
#  'CountyID_y_13', 'CountyName_y_14', 'hispanic_population', 'Year_y_16',
#  'CountyID_x_17', 'CountyName_x_18', 'asian_population', 'Year_x_20',
#  'CountyID_y_21', 'CountyName_y_22', 'aian_population', 'Year_y_24']

# We have multiple CountyID and CountyName columns from different sources.
# Assign them accordingly:

result = pd.DataFrame()

result['CountyID_x'] = j4['CountyID']
result['CountyName_x'] = j4['CountyName_x']
result['whites_population'] = j4['whites_population']
result['Year_x'] = j4['Year']
result['ID'] = j4['ID']

result['CountyID_y'] = j4['CountyID']
result['CountyName_y'] = j4['CountyName_y']
result['other_population'] = j4['other_population']
result['Year_y'] = j4['Year']

result['CountyID_x_9'] = j4['CountyID']
result['CountyName_x_10'] = j4['CountyName_y_10']
result['mixed_population'] = j4['mixed_population']
result['Year_x_12'] = j4['Year']

result['CountyID_y_13'] = j4['CountyID']
result['CountyName_y_14'] = j4['CountyName_y_14']
result['hispanic_population'] = j4['hispanic_population']
result['Year_y_16'] = j4['Year']

result['CountyID_x_17'] = j4['CountyID']
result['CountyName_x_18'] = j4['CountyName_x_18']
result['asian_population'] = j4['asian_population']
result['Year_x_20'] = j4['Year']

result['CountyID_y_21'] = j4['CountyID']
result['CountyName_y_22'] = j4['CountyName_y_22']
result['aian_population'] = j4['aian_population']
result['Year_y_24'] = j4['Year']

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_27/target_multisource_mcts.csv", index=False)