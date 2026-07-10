import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_3.csv", index_col=0)

joined_0 = pd.merge(df0, df1, how='inner', on=['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome'], suffixes=('_0', '_1'))

# After join, columns from df0 and df1 coexist. We keep columns from df0 except Deaths and PolityName from df0,
# but Deaths and PolityName are only in df0, not in df1. df1 has no PolityName.
# The join keys and columns are the same, so the join will duplicate columns with suffixes for non-join columns.
# Actually, all columns except PolityName and Deaths are join keys or in both tables.
# PolityName only in df0, Deaths in both, so Deaths will be suffixed.
# We want to keep Deaths from df0 (Deaths_0) and PolityName from df0.
# So select columns accordingly.

joined_0 = joined_0.rename(columns={
    'Deaths_0': 'Deaths',
    'PolityName': 'PolityName'
})

# Select columns for the target schema from joined_0:
cols = ['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']
joined_0 = joined_0[cols]

# df2 and df3 have the same schema as df0 (including PolityName and Deaths).
# We need to union joined_0, df2, and df3.
# But joined_0 has no NaNs in PolityName or Deaths, df2 and df3 may have NaNs.
# We just concat them.

df2 = df2[cols]
df3 = df3[cols]

result = pd.concat([joined_0, df2, df3], ignore_index=True)

# Fix data types according to target schema:
# Side: string
result['Side'] = result['Side'].astype(str)
# WarID, PolityID, StartYear, StartMonth, StartDay, EndYear, EndMonth, EndDay, IsInitiator, Outcome, Deaths, PolityName: integer
int_cols = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']
for c in int_cols:
    result[c] = pd.to_numeric(result[c], errors='coerce').fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_51/target_multisource_mcts.csv", index=False)