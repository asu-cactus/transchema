import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_3.csv", index_col=0)

# Target columns
target_cols = ['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']

# s2 lacks PolityName, add it with NaN (or empty string)
s2 = s2.copy()
s2['PolityName'] = pd.NA

# Ensure all sources have all target columns (some may have extra columns, drop them)
def align_columns(df):
    # Add missing columns with NA
    for col in target_cols:
        if col not in df.columns:
            df[col] = pd.NA
    # Select only target columns in order
    return df[target_cols]

s0_aligned = align_columns(s0)
s1_aligned = align_columns(s1)
s2_aligned = align_columns(s2)
s3_aligned = align_columns(s3)

# Concatenate all sources
df_all = pd.concat([s0_aligned, s1_aligned, s2_aligned, s3_aligned], ignore_index=True)

# Convert columns to appropriate types before aggregation
# PolityName as string (keep NaN as is)
df_all['PolityName'] = df_all['PolityName'].astype('string')

# For integer columns, convert to numeric with coercion
int_cols = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']

for col in int_cols:
    df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

# Group by the leftmost columns that form unique key in target
group_cols = ['PolityName', 'WarID', 'PolityID']

# Aggregations:
# For date columns: min for start dates, max for end dates
# For Side, IsInitiator, Outcome: min (assuming consistent)
# For Deaths: sum
agg_dict = {
    'StartYear': 'min',
    'StartMonth': 'min',
    'StartDay': 'min',
    'EndYear': 'max',
    'EndMonth': 'max',
    'EndDay': 'max',
    'Side': 'min',
    'IsInitiator': 'min',
    'Outcome': 'min',
    'Deaths': 'sum'
}

df_grouped = df_all.groupby(group_cols, dropna=False, as_index=False).agg(agg_dict)

# After aggregation, ensure types are int (fill NaN with 0)
for col in int_cols:
    if col != 'Deaths':  # Deaths sum can be float if NaN present, fillna(0) then convert
        df_grouped[col] = df_grouped[col].fillna(0).astype(int)
    else:
        # Deaths sum: fillna(0) and convert to int
        df_grouped[col] = df_grouped[col].fillna(0).astype(int)

# PolityName: keep as string, fill NaN with empty string or keep as is
df_grouped['PolityName'] = df_grouped['PolityName'].fillna('').astype(str)

# Reorder columns to target_cols (should already be in order)
df_grouped = df_grouped[target_cols]

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv", index=False)