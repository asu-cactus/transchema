import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_55/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_55/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_55/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_55/training_3.csv", index_col=0)

agg = pd.DataFrame()
agg['Year'] = s1['Year']
agg['CountyName'] = s3['CountyName']

agg = pd.merge(s0, s1, on=['Year', 'CountyName'], how='outer', suffixes=('_0', '_1'))
agg = pd.merge(agg, s2, on=['Year', 'CountyName'], how='outer')
agg = pd.merge(agg, s3, on=['Year', 'CountyName'], how='outer', suffixes=('_2', '_3'))

# The partial plan suggests a group by Year and CountyName with sum aggregations on population columns.
# But the target schema has multiple CountyID_x, CountyName_x, CountyID_y, CountyName_y, etc. columns.
# The target schema columns suggest that the final table is a join of all source tables on Year and CountyName,
# preserving all columns from each source with suffixes.

# To achieve this, we join all source tables on Year and CountyName, keeping all columns,
# then rename columns to match the target schema.

# Join s0 and s1 on Year and CountyName with suffixes _x and _y
df01 = pd.merge(s0, s1, on=['Year', 'CountyName'], how='outer', suffixes=('_x', '_y'))

# Join df01 with s2 on Year and CountyName, suffixes for s2 columns
df012 = pd.merge(df01, s2, on=['Year', 'CountyName'], how='outer', suffixes=('', '_9'))

# Join df012 with s3 on Year and CountyName, suffixes for s3 columns
df0123 = pd.merge(df012, s3, on=['Year', 'CountyName'], how='outer', suffixes=('_12', '_13'))

# Now rename columns to match target schema exactly:
# Target schema:
# ['CountyID_x': int, 'CountyName_x': str, 'whites_population': int, 'Year_x': int, 'ID': int,
#  'CountyID_y': int, 'CountyName_y': str, 'other_population': int, 'Year_y': int,
#  'CountyID_x_9': int, 'CountyName_x_10': str, 'mixed_population': int, 'Year_x_12': int,
#  'CountyID_y_13': int, 'CountyName_y_14': str, 'aian_population': int, 'Year_y_16': int]

# The suffixes from merges:
# s0 columns: CountyID, CountyName, whites_population, Year, ID
# s1 columns: CountyID, CountyName, other_population, Year, ID
# s2 columns: CountyID, CountyName, mixed_population, Year, ID
# s3 columns: CountyID, CountyName, aian_population, Year, ID

# After merges:
# s0 columns have suffix _x
# s1 columns have suffix _y
# s2 columns have suffix _9 (from suffixes=('', '_9') in merge with s2)
# s3 columns have suffix _13 (from suffixes=('_12', '_13') in merge with s3)

# But the last merge used suffixes=('_12', '_13'), so s2 columns got _12 suffix, s3 columns got _13 suffix.
# We need to fix this carefully.

# Let's do merges stepwise with explicit suffixes to match target schema:

s0_ = s0.add_suffix('_x')
s1_ = s1.add_suffix('_y')
s2_ = s2.add_suffix('_x_9')
s3_ = s3.add_suffix('_y_13')

# Year columns are duplicated, so keep one copy per source with suffixes:
# Rename Year columns in each to match target schema:
s0_ = s0_.rename(columns={'Year_x': 'Year_x', 'CountyName_x': 'CountyName_x', 'CountyID_x': 'CountyID_x', 'ID_x': 'ID'})
s1_ = s1_.rename(columns={'Year_y': 'Year_y', 'CountyName_y': 'CountyName_y', 'CountyID_y': 'CountyID_y', 'ID_y': 'ID_y'})
s2_ = s2_.rename(columns={'Year_x_9': 'Year_x_12', 'CountyName_x_9': 'CountyName_x_10', 'CountyID_x_9': 'CountyID_x_9', 'ID_x_9': 'ID_x_9'})
s3_ = s3_.rename(columns={'Year_y_13': 'Year_y_16', 'CountyName_y_13': 'CountyName_y_14', 'CountyID_y_13': 'CountyID_y_13', 'ID_y_13': 'ID_y_13'})

# Now join all on Year and CountyName (using the original columns without suffixes for join keys)
# But after suffixing, original columns are renamed, so we need to keep original columns for join keys.

# Extract join keys from original dataframes before suffixing:
keys_s0 = s0[['Year', 'CountyName']]
keys_s1 = s1[['Year', 'CountyName']]
keys_s2 = s2[['Year', 'CountyName']]
keys_s3 = s3[['Year', 'CountyName']]

# Add keys to suffixed dataframes for join:
s0_['Year'] = keys_s0['Year']
s0_['CountyName'] = keys_s0['CountyName']
s1_['Year'] = keys_s1['Year']
s1_['CountyName'] = keys_s1['CountyName']
s2_['Year'] = keys_s2['Year']
s2_['CountyName'] = keys_s2['CountyName']
s3_['Year'] = keys_s3['Year']
s3_['CountyName'] = keys_s3['CountyName']

# Join s0_ and s1_ on Year and CountyName
df01 = pd.merge(s0_, s1_, on=['Year', 'CountyName'], how='outer')

# Join df01 and s2_
df012 = pd.merge(df01, s2_, on=['Year', 'CountyName'], how='outer')

# Join df012 and s3_
df0123 = pd.merge(df012, s3_, on=['Year', 'CountyName'], how='outer')

# Drop the extra join keys Year and CountyName (original) because target schema has Year_x, Year_y, etc.
df0123 = df0123.drop(columns=['Year', 'CountyName'])

# Reorder columns to match target schema exactly:
final_cols = [
    'CountyID_x', 'CountyName_x', 'whites_population', 'Year_x', 'ID',
    'CountyID_y', 'CountyName_y', 'other_population', 'Year_y',
    'CountyID_x_9', 'CountyName_x_10', 'mixed_population', 'Year_x_12',
    'CountyID_y_13', 'CountyName_y_14', 'aian_population', 'Year_y_16'
]

# Some columns may be missing if source data is incomplete, fill missing columns with NaN
for col in final_cols:
    if col not in df0123.columns:
        df0123[col] = pd.NA

df_final = df0123[final_cols]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length3_55/target_multisource_mcts.csv", index=False)