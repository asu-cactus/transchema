import pandas as pd

# Read all source CSVs with index_col=0 as per hint 22
src0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_52/training_0.csv', index_col=0)
src1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_52/training_1.csv', index_col=0)
src2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_52/training_2.csv', index_col=0)
src3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_52/training_3.csv', index_col=0)

# Source3 lacks PolityName column, add it with NaN to align schemas
if 'PolityName' not in src3.columns:
    src3['PolityName'] = pd.NA

# Concatenate all sources (UNION)
df = pd.concat([src0, src1, src2, src3], ignore_index=True, sort=False)

# Define group by columns (leftmost integer columns in target schema, excluding Deaths and PolityName)
group_by_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
                 'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome']

# Aggregate Deaths by sum, PolityName by first non-null value
agg_dict = {
    'Deaths': 'sum',
    'PolityName': 'first'
}

# Group by and aggregate
grouped = df.groupby(group_by_cols, dropna=False).agg(agg_dict).reset_index()

# PolityName is string in source but integer in target, encode it as integer codes
# Factorize PolityName, missing values get code -1, replace with NaN then fill with 0 or keep NaN
codes, uniques = pd.factorize(grouped['PolityName'])
# Replace -1 with NaN to keep missing as NaN
codes = pd.Series(codes).replace(-1, pd.NA)
grouped['PolityName'] = codes

# Convert all columns to integer type as per target schema
# Some columns may have NaN, so use Int64 dtype (nullable integer)
int_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

for col in int_cols:
    grouped[col] = pd.to_numeric(grouped[col], errors='coerce').astype('Int64')

# Reorder columns to match target schema exactly
target_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

grouped = grouped[target_cols]

# Write output CSV
grouped.to_csv('autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv', index=False)