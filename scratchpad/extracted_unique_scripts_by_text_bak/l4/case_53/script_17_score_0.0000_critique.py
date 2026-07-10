import pandas as pd

# Read source CSVs with index_col=0 as per hint 22
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_3.csv", index_col=0)

# UNION Source4_53_0, Source4_53_1, Source4_53_3 (all have PolityName)
unioned = pd.concat([source0, source1, source3], ignore_index=True)

# Join unioned with Source4_53_2 on all key columns except PolityName (which Source4_53_2 lacks)
join_keys = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
             'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome']

# Perform inner join to keep only matching rows (to avoid duplicates and missing data)
joined = pd.merge(unioned, source2, on=join_keys, how='inner', suffixes=('', '_src2'))

# For Deaths, sum the Deaths from unioned and source2 if needed.
# But since Deaths is present in both, and source2 might have more accurate data,
# we take the Deaths from source2 if available, else from unioned.
# However, since we do aggregation later, we can sum both Deaths columns.

# Create a Deaths column summing both Deaths columns (handle NaNs)
joined['Deaths'] = joined['Deaths'].fillna(0) + joined['Deaths_src2'].fillna(0)

# Drop the extra Deaths_src2 column
joined = joined.drop(columns=['Deaths_src2'])

# Group by PolityName, WarID, PolityID and aggregate Deaths by sum
group_cols = ['PolityName', 'WarID', 'PolityID']

# For other columns in target schema (StartYear, StartMonth, etc.), take first value (assuming consistent per group)
agg_dict = {
    'StartYear': 'first',
    'StartMonth': 'first',
    'StartDay': 'first',
    'EndYear': 'first',
    'EndMonth': 'first',
    'EndDay': 'first',
    'Side': 'first',
    'IsInitiator': 'first',
    'Outcome': 'first',
    'Deaths': 'sum'
}

result = joined.groupby(group_cols, as_index=False).agg(agg_dict)

# Ensure column order matches target schema exactly
target_columns = ['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
                  'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']

result = result[target_columns]

# Convert columns to correct types as per target schema
# PolityName: string
result['PolityName'] = result['PolityName'].astype(str)

# The rest are integers, but source data may have floats due to NaNs, so convert carefully
int_cols = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']

for col in int_cols:
    # Fill NaNs with 0 before converting to int (Deaths can be 0 if no data)
    result[col] = result[col].fillna(0).astype(int)

# Write to target CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv", index=False)