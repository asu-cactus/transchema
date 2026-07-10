import pandas as pd

# Read source CSVs with index_col=0 as per hint 22
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_3.csv", index_col=0)

# UNION the first three sources (same schema)
unioned = pd.concat([source0, source1, source2], ignore_index=True)

# Join unioned with source3 on all shared keys
join_keys = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
             'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome']

# Perform inner join to avoid losing rows (Hint 17)
joined = pd.merge(unioned, source3, how='inner', on=join_keys, suffixes=('', '_src3'))

# After join, columns from source3 that are not in unioned are none except possibly PolityName missing in source3
# PolityName is only in unioned, so keep it from unioned

# Prepare final dataframe columns as per target schema:
# ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

# Some columns may be float, convert to int where appropriate (target schema is integer)
# Deaths aggregation: sum

# Group by leftmost columns (all except Deaths)
group_by_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
                 'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'PolityName']

# PolityName is only in unioned, so ensure it is present in joined
# joined has PolityName from unioned (no suffix), so good

# Aggregate sum on Deaths (from unioned and source3, but source3 also has Deaths)
# To avoid confusion, sum Deaths from both sides:
# joined has Deaths (from unioned) and Deaths_src3 (from source3)
# sum them to get total Deaths

joined['Deaths'] = joined['Deaths'].fillna(0) + joined['Deaths_src3'].fillna(0)

# Now group by keys and sum Deaths
result = joined.groupby(group_by_cols, dropna=False, as_index=False).agg({'Deaths': 'sum'})

# Convert all columns to int as per target schema
for col in ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths']:
    # Some columns may have NaN, fill with 0 before converting
    result[col] = result[col].fillna(0).astype(int)

# PolityName is string in source but target expects integer, so convert PolityName to integer by encoding
# The target examples show PolityName as integer, so encode PolityName as categorical codes
result['PolityName'] = result['PolityName'].fillna('')  # fill NaN with empty string
result['PolityName'] = result['PolityName'].astype(str).astype('category').cat.codes

# Write to CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv", index=False)