import pandas as pd

# Read all sources
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_3.csv", index_col=0)

# Define target columns and their types
cols = ['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
        'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']

# Some sources lack PolityName column (df1), so add it with NaN
for df in [df0, df1, df2, df3]:
    # Add missing columns with NaN
    for c in cols:
        if c not in df.columns:
            df[c] = pd.NA

# Select and reorder columns to target schema
df0 = df0[cols]
df1 = df1[cols]
df2 = df2[cols]
df3 = df3[cols]

# Concatenate all sources
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Convert Side to string
df_all['Side'] = df_all['Side'].astype(str)

# Convert numeric columns to numeric, coerce errors, fill NaN with 0, then convert to int
int_cols = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']

for c in int_cols:
    df_all[c] = pd.to_numeric(df_all[c], errors='coerce').fillna(0).astype(int)

# Group by leftmost columns: Side, WarID, PolityID
# Aggregate Deaths by sum
# Aggregate other columns by max (to keep consistent values)
agg_dict = {
    'Deaths': 'sum',
    'StartYear': 'max',
    'StartMonth': 'max',
    'StartDay': 'max',
    'EndYear': 'max',
    'EndMonth': 'max',
    'EndDay': 'max',
    'IsInitiator': 'max',
    'Outcome': 'max',
    'PolityName': 'max'
}

result = df_all.groupby(['Side', 'WarID', 'PolityID'], as_index=False).agg(agg_dict)

# Reorder columns to target schema
result = result[cols]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_51/target_multisource_mcts.csv", index=False)