import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_54/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_54/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_54/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_54/training_3.csv", index_col=0)

agg = pd.DataFrame()
agg['Year'] = s2['Year'].unique()
agg = agg.sort_values('Year').reset_index(drop=True)

agg_whites = s1.groupby('Year', as_index=False)['whites_population'].sum()
agg_other = s2.groupby('Year', as_index=False)['other_population'].sum()
agg_mixed = s0.groupby('Year', as_index=False)['mixed_population'].sum()
agg_black = s3.groupby('Year', as_index=False)['black_population'].sum()

agg = agg.merge(agg_whites, on='Year', how='left')
agg = agg.merge(agg_other, on='Year', how='left')
agg = agg.merge(agg_mixed, on='Year', how='left')
agg = agg.merge(agg_black, on='Year', how='left')

join1 = agg.merge(s1, on='Year', how='left', suffixes=('', '_y'))
join2 = join1.merge(s2, on='Year', how='left', suffixes=('', '_y_2'))
join3 = join2.merge(s0, on='Year', how='left', suffixes=('', '_x_9'))
final = join3.merge(s3, on='Year', how='left', suffixes=('', '_y_13'))

final = final.rename(columns={
    'CountyID': 'CountyID_x',
    'CountyName': 'CountyName_x',
    'whites_population': 'whites_population',
    'Year': 'Year_x',
    'ID': 'ID',
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
    'black_population': 'black_population',
    'Year_y_16': 'Year_y_16'
})

# The merges create multiple columns with similar names; we must assign columns carefully:
# From s0: CountyID, CountyName, mixed_population, Year, ID
# From s1: CountyID, CountyName, whites_population, Year, ID
# From s2: CountyID, CountyName, other_population, Year, ID
# From s3: CountyID, CountyName, black_population, Year, ID

# After merges, columns are suffixed; we must rename and select columns to match target schema exactly.

# Extract columns from each source with suffixes as per merges:
# s1 columns: CountyID, CountyName, whites_population, Year, ID (no suffix)
# s2 columns: CountyID_y, CountyName_y, other_population, Year_y, ID_y
# s0 columns: CountyID_x_9, CountyName_x_10, mixed_population, Year_x_12, ID_x_9
# s3 columns: CountyID_y_13, CountyName_y_14, black_population, Year_y_16, ID_y_13

# Rename columns accordingly:
final = final.rename(columns={
    'CountyID': 'CountyID_x',
    'CountyName': 'CountyName_x',
    'Year': 'Year_x',
    'ID': 'ID',
    'CountyID_y': 'CountyID_y',
    'CountyName_y': 'CountyName_y',
    'Year_y': 'Year_y',
    'CountyID_x_9': 'CountyID_x_9',
    'CountyName_x_10': 'CountyName_x_10',
    'Year_x_12': 'Year_x_12',
    'CountyID_y_13': 'CountyID_y_13',
    'CountyName_y_14': 'CountyName_y_14',
    'Year_y_16': 'Year_y_16'
})

# Select and reorder columns to match target schema exactly:
result = final[[
    'CountyID_x', 'CountyName_x', 'whites_population', 'Year_x', 'ID',
    'CountyID_y', 'CountyName_y', 'other_population', 'Year_y',
    'CountyID_x_9', 'CountyName_x_10', 'mixed_population', 'Year_x_12',
    'CountyID_y_13', 'CountyName_y_14', 'black_population', 'Year_y_16'
]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_54/target_multisource_mcts.csv", index=False)