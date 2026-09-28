import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_56/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_56/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_56/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_56/training_3.csv", index_col=0)

df0_renamed = df0.rename(columns={
    'CountyID': 'CountyID_x',
    'CountyName': 'CountyName_x',
    'whites_population': 'whites_population',
    'Year': 'Year_x',
    'ID': 'ID'
})[['CountyID_x', 'CountyName_x', 'whites_population', 'Year_x', 'ID']]

df1_renamed = df1.rename(columns={
    'CountyID': 'CountyID_y',
    'CountyName': 'CountyName_y',
    'asian_population': 'asian_population',
    'Year': 'Year_y',
    'ID': 'ID'
})[['CountyID_y', 'CountyName_y', 'asian_population', 'Year_y', 'ID']]

df2_renamed = df2.rename(columns={
    'CountyID': 'CountyID_y',
    'CountyName': 'CountyName_y',
    'other_population': 'other_population',
    'Year': 'Year_y',
    'ID': 'ID'
})[['CountyID_y', 'CountyName_y', 'other_population', 'Year_y', 'ID']]

df3_renamed = df3.rename(columns={
    'CountyID': 'CountyID_x_9',
    'CountyName': 'CountyName_x_10',
    'mixed_population': 'mixed_population',
    'Year': 'Year_x_12',
    'ID': 'ID'
})[['CountyID_x_9', 'CountyName_x_10', 'mixed_population', 'Year_x_12', 'ID']]

# First union all source tables vertically by aligning on common columns (CountyID, CountyName, Year, ID) is not possible because columns differ.
# Instead, we join all four tables on CountyID and Year and ID to get all population columns side by side.

# Start by merging df0 and df2 on CountyID and Year and ID to get whites_population and other_population together
df_0_2 = pd.merge(df0, df2, on=['CountyID', 'CountyName', 'Year', 'ID'], how='outer', suffixes=('_x', '_y'))

# Merge df_0_2 with df3 on same keys to add mixed_population
df_0_2_3 = pd.merge(df_0_2, df3, on=['CountyID', 'CountyName', 'Year', 'ID'], how='outer', suffixes=('', '_3'))

# Merge the above with df1 to add asian_population
df_all = pd.merge(df_0_2_3, df1, on=['CountyID', 'CountyName', 'Year', 'ID'], how='outer', suffixes=('', '_1'))

# Now rename columns to match target schema
df_all = df_all.rename(columns={
    'CountyID': 'CountyID_x',
    'CountyName': 'CountyName_x',
    'whites_population': 'whites_population',
    'Year': 'Year_x',
    'ID': 'ID',
    'CountyID_y': 'CountyID_y',
    'CountyName_y': 'CountyName_y',
    'other_population': 'other_population',
    'Year_y': 'Year_y',
    'CountyID_3': 'CountyID_x_9',
    'CountyName_3': 'CountyName_x_10',
    'mixed_population': 'mixed_population',
    'Year_3': 'Year_x_12',
    'CountyID_1': 'CountyID_y_13',
    'CountyName_1': 'CountyName_y_14',
    'asian_population': 'asian_population',
    'Year_1': 'Year_y_16'
})

# Some columns may be missing due to outer join, fill missing columns with NaN or 0 for population columns
for col in ['whites_population', 'other_population', 'mixed_population', 'asian_population']:
    if col not in df_all.columns:
        df_all[col] = 0
    else:
        df_all[col] = df_all[col].fillna(0).astype(int)

# For ID columns, keep as is (string or int)
# For CountyID and Year columns, fill missing with NaN (do not fill with 0)
for col in ['CountyID_x', 'CountyID_y', 'CountyID_x_9', 'CountyID_y_13']:
    if col not in df_all.columns:
        df_all[col] = pd.NA
    else:
        df_all[col] = df_all[col].astype('Int64')

for col in ['Year_x', 'Year_y', 'Year_x_12', 'Year_y_16']:
    if col not in df_all.columns:
        df_all[col] = pd.NA
    else:
        df_all[col] = df_all[col].astype('Int64')

# For CountyName columns, fill missing with empty string
for col in ['CountyName_x', 'CountyName_y', 'CountyName_x_10', 'CountyName_y_14']:
    if col not in df_all.columns:
        df_all[col] = ''
    else:
        df_all[col] = df_all[col].fillna('')

# Reorder columns to match target schema exactly
df_all = df_all[['CountyID_x', 'CountyName_x', 'whites_population', 'Year_x', 'ID',
                 'CountyID_y', 'CountyName_y', 'other_population', 'Year_y',
                 'CountyID_x_9', 'CountyName_x_10', 'mixed_population', 'Year_x_12',
                 'CountyID_y_13', 'CountyName_y_14', 'asian_population', 'Year_y_16']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length3_56/target_multisource_mcts.csv", index=False)