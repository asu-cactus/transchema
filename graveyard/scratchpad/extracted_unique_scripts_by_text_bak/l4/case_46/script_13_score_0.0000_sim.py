import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

join_01 = pd.merge(s1, s0, on="WarID", suffixes=('_1', '_0'))
join_012 = pd.merge(join_01, s2, on="WarID", suffixes=('', '_2'))
join_all = pd.merge(join_012, s3, on="WarID", suffixes=('', '_3'))

df = join_all.copy()

# Resolve WarShortName and WarType columns: prefer s3's WarShortName and WarType if present, else fallback
# Because suffixes added, columns are: WarShortName_1, WarShortName_0, WarShortName, WarShortName_2, WarShortName_3
# But after merges, columns are: WarShortName_1, WarShortName_0, WarShortName (from s2), WarShortName (from s3) replaced original
# Actually, suffixes only added on conflicts, so after last merge, s3 columns have no suffix, s2 columns have no suffix either (merged last)
# To avoid confusion, let's check columns and pick WarShortName from s3 if exists, else from s2, else from s1 or s0

# After merges, columns:
# WarID
# WarShortName_1 (from s1)
# WarType_1 (from s1)
# IsIntervention
# WarShortName_0 (from s0)
# WarType_0 (from s0)
# WarShortName (from s2)
# WarType (from s2)
# WarShortName (from s3) replaced previous WarShortName? No, suffixes=('', '_3') so s3 columns have suffix _3
# So s3 columns are WarShortName_3, WarType_3, IsInternational

# So columns are:
# WarID
# WarShortName_1, WarType_1, IsIntervention
# WarShortName_0, WarType_0
# WarShortName, WarType (from s2)
# WarShortName_3, WarType_3, IsInternational

# We want to pick WarShortName and WarType from s3 if present, else fallback to s2, else fallback to s1 or s0

def coalesce_columns(df, cols):
    for col in cols:
        if col in df.columns:
            if df[col].notna().any():
                return df[col]
    return pd.Series([pd.NA]*len(df))

df['WarShortName_final'] = coalesce_columns(df, ['WarShortName_3', 'WarShortName', 'WarShortName_1', 'WarShortName_0'])
df['WarType_final'] = coalesce_columns(df, ['WarType_3', 'WarType', 'WarType_1', 'WarType_0'])

# Prepare final dataframe with required columns and correct types
result = pd.DataFrame()
result['IsInternational'] = df['IsInternational'].astype('Int64')
result['WarID'] = df['WarID'].astype('Int64')
result['WarShortName'] = pd.to_numeric(df['WarShortName_final'], errors='coerce').astype('Int64')
result['WarType'] = pd.to_numeric(df['WarType_final'], errors='coerce').astype('Int64')
result['IsIntervention'] = df['IsIntervention'].astype('Int64')

# Group by all columns to remove duplicates if any
result = result.groupby(['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention'], dropna=False).size().reset_index().drop(columns=0)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)