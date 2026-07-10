import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_27/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_27/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_27/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_27/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_27/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_27/training_5.csv", index_col=0)

j1 = pd.merge(s3, s5, on=["CountyID", "Year"], suffixes=('_x', '_y'))
j2 = pd.merge(j1, s0, on=["CountyID", "Year"], suffixes=('', '_y'))
j3 = pd.merge(j2, s2, on=["CountyID", "Year"], suffixes=('', '_y'))
j4 = pd.merge(j3, s1, on=["CountyID", "Year"], suffixes=('', '_y'))
j5 = pd.merge(j4, s4, on=["CountyID", "Year"], suffixes=('', '_y'))

df = j5.rename(columns={
    'CountyID': 'CountyID_x',
    'CountyName_x': 'CountyName_x',
    'whites_population': 'whites_population',
    'Year': 'Year_x',
    'ID': 'ID',
    'CountyID_y': 'CountyID_y',
    'CountyName_y': 'CountyName_y',
    'other_population': 'other_population',
    'Year_y': 'Year_y',
    'CountyID_x_y': 'CountyID_x_9',
    'CountyName_x_y': 'CountyName_x_10',
    'mixed_population': 'mixed_population',
    'Year_x_y': 'Year_x_12',
    'CountyID_y_y': 'CountyID_y_13',
    'CountyName_y_y': 'CountyName_y_14',
    'hispanic_population': 'hispanic_population',
    'Year_y_y': 'Year_y_16',
    'CountyID_x_x': 'CountyID_x_17',
    'CountyName_x_x': 'CountyName_x_18',
    'asian_population': 'asian_population',
    'Year_x_x': 'Year_x_20',
    'CountyID_y_x': 'CountyID_y_21',
    'CountyName_y_x': 'CountyName_y_22',
    'aian_population': 'aian_population',
    'Year_y_x': 'Year_y_24'
}, errors='ignore')

cols = [
    'CountyID_x', 'CountyName_x', 'whites_population', 'Year_x', 'ID',
    'CountyID_y', 'CountyName_y', 'other_population', 'Year_y',
    'CountyID_x_9', 'CountyName_x_10', 'mixed_population', 'Year_x_12',
    'CountyID_y_13', 'CountyName_y_14', 'hispanic_population', 'Year_y_16',
    'CountyID_x_17', 'CountyName_x_18', 'asian_population', 'Year_x_20',
    'CountyID_y_21', 'CountyName_y_22', 'aian_population', 'Year_y_24'
]

# Some columns may not exist exactly as above due to suffixes, so we carefully map them:
# After merges, columns from s3 and s5 have suffixes _x and _y respectively in j1
# Then s0 columns added without suffixes, s2 columns added with _y suffix, s1 columns with _y suffix, s4 columns with _y suffix
# So we need to rename columns accordingly to match target schema exactly.

# Let's reconstruct the final dataframe with correct columns and suffixes:

# After first merge (s3 and s5):
# s3 columns: CountyID, CountyName_x, asian_population, Year, ID_x
# s5 columns: CountyID, CountyName_y, aian_population, Year, ID_y

# After second merge with s0 (hispanic_population):
# s0 columns: CountyID, CountyName, hispanic_population, Year, ID

# After third merge with s2 (other_population):
# s2 columns: CountyID, CountyName, other_population, Year, ID

# After fourth merge with s1 (mixed_population):
# s1 columns: CountyID, CountyName, mixed_population, Year, ID

# After fifth merge with s4 (whites_population):
# s4 columns: CountyID, CountyName, whites_population, Year, ID

# To avoid confusion, let's rename columns after each merge to unique names matching target schema:

j1 = pd.merge(s3, s5, on=["CountyID", "Year"], suffixes=('_x', '_y'))
j1 = j1.rename(columns={
    'CountyName_x': 'CountyName_x',
    'asian_population': 'asian_population',
    'ID_x': 'ID_x',
    'CountyName_y': 'CountyName_y',
    'aian_population': 'aian_population',
    'ID_y': 'ID_y'
})

j2 = pd.merge(j1, s0, on=["CountyID", "Year"], suffixes=('', '_0'))
j2 = j2.rename(columns={
    'CountyName': 'CountyName_0',
    'hispanic_population': 'hispanic_population',
    'ID': 'ID_0'
})

j3 = pd.merge(j2, s2, on=["CountyID", "Year"], suffixes=('', '_2'))
j3 = j3.rename(columns={
    'CountyName': 'CountyName_2',
    'other_population': 'other_population',
    'ID': 'ID_2'
})

j4 = pd.merge(j3, s1, on=["CountyID", "Year"], suffixes=('', '_1'))
j4 = j4.rename(columns={
    'CountyName': 'CountyName_1',
    'mixed_population': 'mixed_population',
    'ID': 'ID_1'
})

j5 = pd.merge(j4, s4, on=["CountyID", "Year"], suffixes=('', '_4'))
j5 = j5.rename(columns={
    'CountyName': 'CountyName_4',
    'whites_population': 'whites_population',
    'ID': 'ID_4'
})

# Now build the final dataframe with columns renamed to target schema names:

df_final = pd.DataFrame({
    'CountyID_x': j5['CountyID'],
    'CountyName_x': j5['CountyName_x'],
    'whites_population': j5['whites_population'],
    'Year_x': j5['Year'],
    'ID': j5['ID_0'],  # Use ID from s0 as in target examples
    'CountyID_y': j5['CountyID'],
    'CountyName_y': j5['CountyName_0'],
    'other_population': j5['other_population'],
    'Year_y': j5['Year'],
    'CountyID_x_9': j5['CountyID'],
    'CountyName_x_10': j5['CountyName_1'],
    'mixed_population': j5['mixed_population'],
    'Year_x_12': j5['Year'],
    'CountyID_y_13': j5['CountyID'],
    'CountyName_y_14': j5['CountyName_2'],
    'hispanic_population': j5['hispanic_population'],
    'Year_y_16': j5['Year'],
    'CountyID_x_17': j5['CountyID'],
    'CountyName_x_18': j5['CountyName_x'],
    'asian_population': j5['asian_population'],
    'Year_x_20': j5['Year'],
    'CountyID_y_21': j5['CountyID'],
    'CountyName_y_22': j5['CountyName_y'],
    'aian_population': j5['aian_population'],
    'Year_y_24': j5['Year']
})

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length5_27/target_multisource_mcts.csv", index=False)