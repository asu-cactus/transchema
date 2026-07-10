import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_52/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_3.csv",
]

# Read all sources
df0 = pd.read_csv(paths[0], index_col=0)
df1 = pd.read_csv(paths[1], index_col=0)
df2 = pd.read_csv(paths[2], index_col=0)
df3 = pd.read_csv(paths[3], index_col=0)

# Columns to keep and order as per target schema
cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
        'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

# UNION the first three sources (they have PolityName)
df_union = pd.concat([df0, df1, df2], ignore_index=True)

# Ensure all columns exist in df3 for join (df3 lacks PolityName)
# We'll join on all key columns except Deaths and PolityName
join_keys = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
             'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome']

# Join df_union with df3 on join_keys (inner join)
df_joined = pd.merge(df_union, df3[join_keys + ['Deaths']], on=join_keys, how='inner', suffixes=('_union', '_3'))

# After join, we have two Deaths columns: Deaths_union and Deaths_3
# Sum them to get total Deaths
df_joined['Deaths'] = df_joined['Deaths_union'].fillna(0) + df_joined['Deaths_3'].fillna(0)

# Keep columns as per target schema
df_joined = df_joined[cols]

# Convert PolityName to integer (target schema says integer)
# PolityName is string in sources, convert by factorizing (categorical encoding)
df_joined['PolityName'] = pd.factorize(df_joined['PolityName'])[0].astype('Int64')

# Convert all other columns to integer types as per target schema
for c in cols:
    if c != 'PolityName':
        df_joined[c] = pd.to_numeric(df_joined[c], errors='coerce').astype('Int64')

# GROUP BY the leftmost key columns including PolityName, aggregate Deaths by sum
group_by_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
                 'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'PolityName']

df_final = df_joined.groupby(group_by_cols, dropna=False, as_index=False).agg({'Deaths': 'sum'})

# Convert Deaths to Int64 as well
df_final['Deaths'] = pd.to_numeric(df_final['Deaths'], errors='coerce').astype('Int64')

# Write output
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv", index=False)