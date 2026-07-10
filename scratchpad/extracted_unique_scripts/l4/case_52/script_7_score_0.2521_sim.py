import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_3.csv", index_col=0)

join_cols = ['WarID', 'PolityID', 'StartYear']
s1_3 = pd.merge(s1, s3, how='inner', on=join_cols, suffixes=('_s1', '_s3'))

# After join, columns from s1 and s3 exist; we keep columns from s1 for all except IsInitiator from s3 (to match partial plan)
# But target schema matches s1 columns, so we keep s1 columns only (IsInitiator is same in both, keep s1's)
# Drop duplicated columns from s3 (those with suffix _s3)
drop_cols = [c for c in s1_3.columns if c.endswith('_s3')]
s1_3.drop(columns=drop_cols, inplace=True)

# Rename columns to original names if needed (remove _s1 suffix)
s1_3.columns = [c[:-3] if c.endswith('_s1') else c for c in s1_3.columns]

# Now union s0, s1_3, s2
frames = [s0, s1_3, s2]
df = pd.concat(frames, ignore_index=True, sort=False)

# Ensure target schema columns and types
target_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

# Some columns may be missing or have different types, fix types and order
df = df[target_cols]

# Convert types according to target schema: all integer except Deaths which may be float but target shows integer
# From examples, PolityName is integer (though source has string), so convert PolityName to integer if possible (e.g. categorical codes)
# PolityName in sources is string, target expects integer, so convert PolityName to categorical codes (starting from 1)
df['PolityName'] = df['PolityName'].astype('category').cat.codes + 1

# Convert all other columns to integer where possible, Deaths may have NaN, fill NaN with 0 then convert to int
for col in ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths']:
    if col == 'Deaths':
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    else:
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv", index=False)