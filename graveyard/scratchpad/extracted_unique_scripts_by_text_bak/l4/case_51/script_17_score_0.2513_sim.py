import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_3.csv", index_col=0)

join_cols = ['Side', 'WarID', 'PolityID']
s0_key = s0.set_index(join_cols)
s1_key = s1.set_index(join_cols)

joined = s0_key.join(s1_key, lsuffix='_0', rsuffix='_1', how='inner').reset_index()

# After join, columns from s0 and s1 coexist; s1 lacks PolityName, so take PolityName from s0 only.
# For columns present in both, take from s0 (suffix _0), drop _1 columns except those missing in s0.
# Columns in s0: ['WarID', 'PolityID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']
# Columns in s1: same except no PolityName

# Keep columns from s0, drop duplicates from s1
cols_to_keep = ['Side', 'WarID', 'PolityID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths']
joined = joined[[col if col in joined.columns else col+'_0' for col in cols_to_keep]]

# Rename columns if any have suffix _0
joined.columns = [col.replace('_0','') for col in joined.columns]

# Now unify schemas for union with s2 and s3
# s2 and s3 have PolityName, s1 does not, s0 does
# s1 was joined, so no longer separate
# s2 and s3 have same schema as s0

# For s2 and s3, ensure columns match target schema and types
def prepare_df(df):
    df = df.copy()
    # Ensure all target columns exist
    target_cols = ['Side', 'WarID', 'PolityID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths']
    for c in target_cols:
        if c not in df.columns:
            df[c] = pd.NA
    df = df[target_cols]
    return df

joined = prepare_df(joined)
s2 = prepare_df(s2)
s3 = prepare_df(s3)

# Concatenate all
result = pd.concat([joined, s2, s3], ignore_index=True)

# Convert columns to target types
result['Side'] = result['Side'].astype('string')
int_cols = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']
for c in int_cols:
    result[c] = pd.to_numeric(result[c], errors='coerce').astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_51/target_multisource_mcts.csv", index=False)