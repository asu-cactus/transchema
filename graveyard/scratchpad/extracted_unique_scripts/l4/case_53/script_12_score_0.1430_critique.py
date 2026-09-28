import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_3.csv", index_col=0)

# Join df2 with df0 to get PolityName (df2 lacks PolityName)
df2_joined = pd.merge(
    df2,
    df0[['WarID', 'PolityID', 'PolityName']].drop_duplicates(),
    on=['WarID', 'PolityID'],
    how='left'
)

# Join df3 with df0 to get PolityName (df3 has many NaNs in PolityID and PolityName)
df3_joined = pd.merge(
    df3,
    df0[['WarID', 'PolityID', 'PolityName']].drop_duplicates(),
    on=['WarID', 'PolityID'],
    how='left'
)

# Ensure all dataframes have the same columns in the same order as target schema
target_cols = ['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']

# For df2_joined, reorder columns and fill missing PolityName if any
df2_joined = df2_joined.reindex(columns=['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
                                         'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName'])
# Move PolityName to first column
df2_joined = df2_joined[['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
                         'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']]

# For df3_joined, reorder columns similarly
df3_joined = df3_joined.reindex(columns=['WarID', 'PolityID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay',
                                         'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths'])
df3_joined = df3_joined[target_cols]

# For df0 and df1, reorder columns to target_cols
df0 = df0[target_cols]
df1 = df1[target_cols]

# Concatenate all dataframes
union_df = pd.concat([df0, df1, df2_joined, df3_joined], ignore_index=True)

# Convert columns to appropriate types before grouping to avoid issues
# PolityName as string
union_df['PolityName'] = union_df['PolityName'].astype('string')

# Convert integer columns safely (some may have NaNs)
int_cols = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome']

for col in int_cols:
    union_df[col] = pd.to_numeric(union_df[col], errors='coerce').astype('Int64')

# Deaths: fill NaN with 0 and convert to Int64
union_df['Deaths'] = union_df['Deaths'].fillna(0).astype('Int64')

# Group by the leftmost columns of target schema (keys) and sum Deaths
final_df = union_df.groupby(
    ['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
     'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome'],
    dropna=False,
    as_index=False
)['Deaths'].sum()

# Ensure final_df columns are in target order and types
final_df = final_df[target_cols]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv", index=False)