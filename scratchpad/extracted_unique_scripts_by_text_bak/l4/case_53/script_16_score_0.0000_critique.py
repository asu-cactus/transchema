import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_3.csv", index_col=0)

# UNION s0, s1, s3 (all have PolityName)
union_result = pd.concat([s0, s1, s3], ignore_index=True)

# JOIN union_result with s2 on WarID and PolityID only
merged = pd.merge(
    union_result,
    s2,
    how='inner',
    on=['WarID', 'PolityID'],
    suffixes=('', '_s2')
)

# Select columns for final output, prefer columns from union_result (no suffix)
# Columns in target schema:
cols = [
    'PolityName',
    'WarID',
    'PolityID',
    'StartYear',
    'StartMonth',
    'StartDay',
    'EndYear',
    'EndMonth',
    'EndDay',
    'Side',
    'IsInitiator',
    'Outcome',
    'Deaths'
]

# For columns that exist in both tables, take from union_result (no suffix)
# For columns missing in union_result but present in s2, take from s2 (with _s2 suffix)
# Check which columns are missing in union_result but present in s2:
# s2 does not have PolityName, so keep from union_result
# For other columns, union_result and s2 have same columns except PolityName

# Construct final DataFrame
df = pd.DataFrame()
df['PolityName'] = merged['PolityName']
df['WarID'] = merged['WarID']
df['PolityID'] = merged['PolityID']

# For the rest columns, prefer union_result columns if not null, else fallback to s2 columns
for col in cols[3:]:
    if col in merged.columns:
        df[col] = merged[col]
    elif col + '_s2' in merged.columns:
        df[col] = merged[col + '_s2']
    else:
        # If column missing in both, fill with NaN
        df[col] = pd.NA

# Convert types according to target schema
df['PolityName'] = df['PolityName'].astype(str)
df['WarID'] = pd.to_numeric(df['WarID'], errors='coerce').astype('Int64')
df['PolityID'] = pd.to_numeric(df['PolityID'], errors='coerce').astype('Int64')
df['StartYear'] = pd.to_numeric(df['StartYear'], errors='coerce').astype('Int64')
df['StartMonth'] = pd.to_numeric(df['StartMonth'], errors='coerce').astype('Int64')
df['StartDay'] = pd.to_numeric(df['StartDay'], errors='coerce').astype('Int64')
df['EndYear'] = pd.to_numeric(df['EndYear'], errors='coerce').astype('Int64')
df['EndMonth'] = pd.to_numeric(df['EndMonth'], errors='coerce').astype('Int64')
df['EndDay'] = pd.to_numeric(df['EndDay'], errors='coerce').astype('Int64')
df['Side'] = pd.to_numeric(df['Side'], errors='coerce').astype('Int64')
df['IsInitiator'] = pd.to_numeric(df['IsInitiator'], errors='coerce').astype('Int64')
df['Outcome'] = pd.to_numeric(df['Outcome'], errors='coerce').astype('Int64')
df['Deaths'] = pd.to_numeric(df['Deaths'], errors='coerce').astype('Int64')

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv", index=False)