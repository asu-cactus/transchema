import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_27/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_27/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_27/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_27/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_27/training_4.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_27/training_5.csv", index_col=0)

df_list = [src0, src1, src2, src3, src4, src5]

# All sources have columns: CountyID, CountyName, Year, ID plus one population column each
# We need to join them on CountyID, CountyName, Year, ID to get all population columns in one row

# Rename columns to avoid collision except keys
def rename_pop_col(df):
    pop_cols = [c for c in df.columns if c not in ['CountyID', 'CountyName', 'Year', 'ID']]
    if len(pop_cols) == 1:
        pop_col = pop_cols[0]
        # rename population column to unique name (keep original name)
        return df.rename(columns={pop_col: pop_col})
    return df

dfs_renamed = [rename_pop_col(df) for df in df_list]

# Merge all on keys: CountyID, CountyName, Year, ID
from functools import reduce

keys = ['CountyID', 'CountyName', 'Year', 'ID']
df_merged = reduce(lambda left, right: pd.merge(left, right, on=keys, how='outer'), dfs_renamed)

# Now rename columns to match target schema exactly
# Target schema:
# ['CountyID_x', 'CountyName_x', 'whites_population', 'Year_x', 'ID',
#  'CountyID_y', 'CountyName_y', 'other_population', 'Year_y',
#  'CountyID_x_9', 'CountyName_x_10', 'mixed_population', 'Year_x_12',
#  'CountyID_y_13', 'CountyName_y_14', 'hispanic_population', 'Year_y_16',
#  'CountyID_x_17', 'CountyName_x_18', 'asian_population', 'Year_x_20',
#  'CountyID_y_21', 'CountyName_y_22', 'aian_population', 'Year_y_24']

# The pattern is that each population column is accompanied by CountyID, CountyName, Year columns with suffixes
# The order of population columns in sources is:
# Source0: hispanic_population
# Source1: mixed_population
# Source2: other_population
# Source3: asian_population
# Source4: whites_population
# Source5: aian_population

# We will create columns accordingly by duplicating keys for each population column group

# Extract keys and population columns from merged df
# keys columns: CountyID, CountyName, Year, ID
# population columns: hispanic_population, mixed_population, other_population, asian_population, whites_population, aian_population

# Create a helper function to duplicate keys with suffixes
def duplicate_keys(df, suffix):
    return df[['CountyID', 'CountyName', 'Year']].rename(columns={
        'CountyID': f'CountyID{suffix}',
        'CountyName': f'CountyName{suffix}',
        'Year': f'Year{suffix}'
    })

# Build the final DataFrame columns in order

# Start with ID column (only one ID column)
final_df = pd.DataFrame()
final_df['ID'] = df_merged['ID']

# whites_population group (from Source4)
final_df['CountyID_x'] = df_merged['CountyID']
final_df['CountyName_x'] = df_merged['CountyName']
final_df['whites_population'] = df_merged['whites_population']
final_df['Year_x'] = df_merged['Year']

# other_population group (from Source2)
final_df['CountyID_y'] = df_merged['CountyID']
final_df['CountyName_y'] = df_merged['CountyName']
final_df['other_population'] = df_merged['other_population']
final_df['Year_y'] = df_merged['Year']

# mixed_population group (from Source1)
final_df['CountyID_x_9'] = df_merged['CountyID']
final_df['CountyName_x_10'] = df_merged['CountyName']
final_df['mixed_population'] = df_merged['mixed_population']
final_df['Year_x_12'] = df_merged['Year']

# hispanic_population group (from Source0)
final_df['CountyID_y_13'] = df_merged['CountyID']
final_df['CountyName_y_14'] = df_merged['CountyName']
final_df['hispanic_population'] = df_merged['hispanic_population']
final_df['Year_y_16'] = df_merged['Year']

# asian_population group (from Source3)
final_df['CountyID_x_17'] = df_merged['CountyID']
final_df['CountyName_x_18'] = df_merged['CountyName']
final_df['asian_population'] = df_merged['asian_population']
final_df['Year_x_20'] = df_merged['Year']

# aian_population group (from Source5)
final_df['CountyID_y_21'] = df_merged['CountyID']
final_df['CountyName_y_22'] = df_merged['CountyName']
final_df['aian_population'] = df_merged['aian_population']
final_df['Year_y_24'] = df_merged['Year']

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_27/target_multisource_mcts.csv", index=False)