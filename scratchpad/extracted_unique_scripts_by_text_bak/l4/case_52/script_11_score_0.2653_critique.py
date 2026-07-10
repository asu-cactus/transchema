import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_3.csv", index_col=0)

# All sources have same schema except s3 missing PolityName, so add PolityName column to s3 with NaN
if 'PolityName' not in s3.columns:
    s3['PolityName'] = pd.NA

# Concatenate all sources (UNION)
df = pd.concat([s0, s1, s2, s3], ignore_index=True, sort=False)

# Target columns and order
target_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

# Keep only target columns (some may have NaN)
df = df[target_cols]

# Convert PolityName to categorical codes starting from 1 (target expects integer)
df['PolityName'] = df['PolityName'].astype('category').cat.codes + 1

# Define group by columns (all except Deaths)
group_by_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
                 'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'PolityName']

# Aggregate Deaths by sum
df_agg = df.groupby(group_by_cols, dropna=False, observed=False, as_index=False).agg({'Deaths': 'sum'})

# Convert columns to integer types as per target schema
# Deaths: fill NaN with 0 then int
df_agg['Deaths'] = pd.to_numeric(df_agg['Deaths'], errors='coerce').fillna(0).astype(int)

# Other columns to integer nullable type Int64 (to allow NaN)
for col in group_by_cols:
    df_agg[col] = pd.to_numeric(df_agg[col], errors='coerce').astype('Int64')

# Reorder columns to target schema
df_agg = df_agg[target_cols]

# Write output
df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv", index=False)