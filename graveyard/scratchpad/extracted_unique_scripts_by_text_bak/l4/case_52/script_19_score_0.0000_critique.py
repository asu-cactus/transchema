import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_3.csv", index_col=0)

# Union s0, s1, s2 (all have PolityName)
union_012 = pd.concat([s0, s1, s2], ignore_index=True, sort=False)

# Key columns for join with s3 (which lacks PolityName)
join_keys = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side']

# Join union_012 with s3 on key columns
joined = pd.merge(
    union_012,
    s3,
    how='inner',
    on=join_keys,
    suffixes=('', '_s3')
)

# Columns to keep (target schema)
cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
        'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

# Prepare dataframe with needed columns
# Some columns may be duplicated from s3 (e.g., IsInitiator_s3), keep from union_012 (no suffix)
# If any column missing, fill with NaN (unlikely)
result = joined[cols].copy()

# Convert columns to numeric as needed (target schema all integers)
for c in cols:
    # PolityName is string in sources, but integer in target, try to convert
    result[c] = pd.to_numeric(result[c], errors='coerce')

# Group by all leftmost integer columns except Deaths (which is aggregated by sum)
group_by_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
                 'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'PolityName']

agg_dict = {'Deaths': 'sum'}

result = result.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# Convert all columns to integer type (Deaths sum may be float)
for c in result.columns:
    # If column is float but all values are integer-like, convert to int
    if pd.api.types.is_float_dtype(result[c]):
        if result[c].isnull().any():
            # If NaNs exist, keep float
            continue
        if (result[c] % 1 == 0).all():
            result[c] = result[c].astype('Int64')  # nullable integer
    elif pd.api.types.is_integer_dtype(result[c]):
        result[c] = result[c].astype('Int64')

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv", index=False)