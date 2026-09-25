import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_52/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_3.csv"
]

# Read sources
df0 = pd.read_csv(paths[0], index_col=0)
df1 = pd.read_csv(paths[1], index_col=0)
df2 = pd.read_csv(paths[2], index_col=0)
df3 = pd.read_csv(paths[3], index_col=0)

# UNION Sources 0,1,2 (all have PolityName as string)
df_union = pd.concat([df0, df1, df2], ignore_index=True)

# Convert PolityName string to integer codes (factorize)
# This ensures PolityName is integer as in target schema
df_union['PolityName'], uniques = pd.factorize(df_union['PolityName'])

# Convert columns to appropriate types (int64 with nullable Int64 for NaNs)
int_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

for col in int_cols:
    # Deaths can have NaN, convert to float first then Int64
    df_union[col] = pd.to_numeric(df_union[col], errors='coerce').astype('Int64')

# Source3 lacks PolityName, convert its columns to int as well
for col in df3.columns:
    df3[col] = pd.to_numeric(df3[col], errors='coerce').astype('Int64')

# JOIN unioned_sources with Source3 on WarID and PolityID
df_joined = pd.merge(df_union, df3, on=['WarID', 'PolityID'], suffixes=('_u', '_3'), how='inner')

# After join, columns from df3 have suffix _3, from union have _u
# We want to keep columns from union (with PolityName) and columns from df3 that are missing in union
# But schemas are mostly same except PolityName missing in df3
# So we can drop duplicate columns from df3 (except those not in union)
# Columns to keep: from union (without suffix), plus any columns only in df3 (none here)
# So drop columns with _3 suffix except those not in union (none)
cols_to_drop = [c for c in df_joined.columns if c.endswith('_3')]
df_joined.drop(columns=cols_to_drop, inplace=True)

# Rename columns to remove _u suffix
df_joined.columns = [c[:-2] if c.endswith('_u') else c for c in df_joined.columns]

# Now group by all leftmost columns except Deaths (which is aggregated by sum)
group_by_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
                 'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'PolityName']

# Aggregations:
# Deaths: sum
# Other columns: take first (assuming consistent per group)
agg_dict = {col: 'first' for col in group_by_cols}
agg_dict['Deaths'] = 'sum'

df_final = df_joined.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# Ensure all columns are Int64 dtype (nullable integer)
for col in df_final.columns:
    df_final[col] = pd.to_numeric(df_final[col], errors='coerce').astype('Int64')

# Write output
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv", index=False)