import pandas as pd

# Read source CSVs
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_55/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_55/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_55/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_55/training_3.csv", index_col=0)

# Join s0 and s1 on CountyID, CountyName, Year (inner join to match only common rows)
df01 = pd.merge(
    s0, s1,
    on=['CountyID', 'CountyName', 'Year'],
    how='inner',
    suffixes=('_x', '_y')
)

# Join df01 and s2 on CountyID, CountyName, Year
df012 = pd.merge(
    df01, s2,
    on=['CountyID', 'CountyName', 'Year'],
    how='inner',
    suffixes=('', '_x_9')
)

# Join df012 and s3 on CountyID, CountyName, Year
df0123 = pd.merge(
    df012, s3,
    on=['CountyID', 'CountyName', 'Year'],
    how='inner',
    suffixes=('', '_y_13')
)

# Rename columns to match target schema exactly
# Target schema:
# ['CountyID_x', 'CountyName_x', 'whites_population', 'Year_x', 'ID',
#  'CountyID_y', 'CountyName_y', 'other_population', 'Year_y',
#  'CountyID_x_9', 'CountyName_x_10', 'mixed_population', 'Year_x_12',
#  'CountyID_y_13', 'CountyName_y_14', 'aian_population', 'Year_y_16']

# Current columns after merges:
# From s0: CountyID, CountyName, whites_population, Year, ID
# From s1: CountyID_y, CountyName_y, other_population, Year_y, ID_y
# From s2: CountyID_x_9, CountyName_x_10, mixed_population, Year_x_12, ID_x_9
# From s3: CountyID_y_13, CountyName_y_14, aian_population, Year_y_16, ID_y_13

# Rename s0 columns to *_x
df0123 = df0123.rename(columns={
    'CountyID': 'CountyID_x',
    'CountyName': 'CountyName_x',
    'Year': 'Year_x',
    'ID': 'ID',
    'Year_y': 'Year_y',
    'Year_x_12': 'Year_x_12',
    'Year_y_16': 'Year_y_16',
    'ID_y': 'ID_y',
    'ID_x_9': 'ID_x_9',
    'ID_y_13': 'ID_y_13'
})

# The ID columns are not in target schema except 'ID' (from s0), so we keep only 'ID' from s0 and drop others
df0123 = df0123.drop(columns=['ID_y', 'ID_x_9', 'ID_y_13'], errors='ignore')

# Reorder columns to match target schema exactly
final_cols = [
    'CountyID_x', 'CountyName_x', 'whites_population', 'Year_x', 'ID',
    'CountyID_y', 'CountyName_y', 'other_population', 'Year_y',
    'CountyID_x_9', 'CountyName_x_10', 'mixed_population', 'Year_x_12',
    'CountyID_y_13', 'CountyName_y_14', 'aian_population', 'Year_y_16'
]

# Some columns might be missing if source data incomplete, add them with NaN
for col in final_cols:
    if col not in df0123.columns:
        df0123[col] = pd.NA

df_final = df0123[final_cols]

# Write output CSV
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length3_55/target_multisource_mcts.csv", index=False)