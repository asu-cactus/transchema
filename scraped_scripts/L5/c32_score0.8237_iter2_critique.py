import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_32/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_32/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_32/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_32/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_32/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_32/training_5.csv", index_col=0)

# Join all on keys: CountyID, CountyName, Year, ID
df = pd.merge(s3, s5, on=['CountyID', 'CountyName', 'Year', 'ID'], how='inner')
df = pd.merge(df, s4, on=['CountyID', 'CountyName', 'Year', 'ID'], how='inner')
df = pd.merge(df, s2, on=['CountyID', 'CountyName', 'Year', 'ID'], how='inner')
df = pd.merge(df, s0, on=['CountyID', 'CountyName', 'Year', 'ID'], how='inner')
df = pd.merge(df, s1, on=['CountyID', 'CountyName', 'Year', 'ID'], how='inner')

# Rename columns to match target schema exactly
# Target schema:
# ['CountyID_x', 'CountyName_x', 'whites_population', 'Year_x', 'ID',
#  'CountyID_y', 'CountyName_y', 'other_population', 'Year_y',
#  'CountyID_x_9', 'CountyName_x_10', 'mixed_population', 'Year_x_12',
#  'CountyID_y_13', 'CountyName_y_14', 'black_population', 'Year_y_16',
#  'CountyID_x_17', 'CountyName_x_18', 'asian_population', 'Year_x_20',
#  'CountyID_y_21', 'CountyName_y_22', 'aian_population', 'Year_y_24']

# We have keys and population columns from each source:
# s3: whites_population
# s5: other_population
# s4: mixed_population
# s2: black_population
# s0: asian_population
# s1: aian_population

# The target schema repeats keys multiple times with different suffixes.
# We replicate keys accordingly.

df = df.rename(columns={
    'CountyID': 'CountyID_x',
    'CountyName': 'CountyName_x',
    'whites_population': 'whites_population',
    'Year': 'Year_x',
    'ID': 'ID',
    'other_population': 'other_population',
    'mixed_population': 'mixed_population',
    'black_population': 'black_population',
    'asian_population': 'asian_population',
    'aian_population': 'aian_population'
})

# Add duplicated key columns to match target schema
df['CountyID_y'] = df['CountyID_x']
df['CountyName_y'] = df['CountyName_x']
df['Year_y'] = df['Year_x']

df['CountyID_x_9'] = df['CountyID_x']
df['CountyName_x_10'] = df['CountyName_x']
df['Year_x_12'] = df['Year_x']

df['CountyID_y_13'] = df['CountyID_x']
df['CountyName_y_14'] = df['CountyName_x']
df['Year_y_16'] = df['Year_x']

df['CountyID_x_17'] = df['CountyID_x']
df['CountyName_x_18'] = df['CountyName_x']
df['Year_x_20'] = df['Year_x']

df['CountyID_y_21'] = df['CountyID_x']
df['CountyName_y_22'] = df['CountyName_x']
df['Year_y_24'] = df['Year_x']

# Reorder columns exactly as target schema
df = df[[
    'CountyID_x', 'CountyName_x', 'whites_population', 'Year_x', 'ID',
    'CountyID_y', 'CountyName_y', 'other_population', 'Year_y',
    'CountyID_x_9', 'CountyName_x_10', 'mixed_population', 'Year_x_12',
    'CountyID_y_13', 'CountyName_y_14', 'black_population', 'Year_y_16',
    'CountyID_x_17', 'CountyName_x_18', 'asian_population', 'Year_x_20',
    'CountyID_y_21', 'CountyName_y_22', 'aian_population', 'Year_y_24'
]]

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length5_32/target_multisource_mcts.csv", index=False)