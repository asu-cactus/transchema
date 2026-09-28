import pandas as pd

# Read all sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

# Join s0 and s1 on WarID with outer join to keep all rows
join_01 = pd.merge(s0, s1, on="WarID", how="outer", suffixes=('_0', '_1'))

# Join the above with s2 on WarID, outer join
join_012 = pd.merge(join_01, s2, on="WarID", how="outer", suffixes=('', '_2'))

# Join the above with s3 on WarID, outer join
join_all = pd.merge(join_012, s3, on="WarID", how="outer", suffixes=('', '_3'))

df = join_all.copy()

# Coalesce WarShortName columns in priority: s3, s2, s1, s0
def coalesce_columns(df, cols):
    for col in cols:
        if col in df.columns:
            # Return the first non-null column series
            non_null = df[col].notna()
            if non_null.any():
                return df[col].where(non_null, pd.NA)
    # If none found, return all NA
    return pd.Series([pd.NA]*len(df), index=df.index)

df['WarShortName_final'] = df['WarShortName_3'].combine_first(
    df['WarShortName']).combine_first(
    df['WarShortName_1']).combine_first(
    df['WarShortName_0'])

df['WarType_final'] = df['WarType_3'].combine_first(
    df['WarType']).combine_first(
    df['WarType_1']).combine_first(
    df['WarType_0'])

# Prepare final dataframe with required columns and correct types
result = pd.DataFrame()
# IsInternational from s3 (suffix _3), may have NaN if missing, fill with 0 as per hint 24
result['IsInternational'] = df['IsInternational'].fillna(0).astype('Int64')
result['WarID'] = df['WarID'].astype('Int64')

# WarShortName and WarType are strings in sources, but target schema says integer
# The target examples show WarShortName and WarType as integers (probably IDs)
# So convert to numeric, coercing errors to NaN, then to Int64
result['WarShortName'] = pd.to_numeric(df['WarShortName_final'], errors='coerce').astype('Int64')
result['WarType'] = pd.to_numeric(df['WarType_final'], errors='coerce').astype('Int64')

# IsIntervention from s1, fill NaN with 0 as per hint 24
result['IsIntervention'] = df['IsIntervention'].fillna(0).astype('Int64')

# No group by or aggregation needed, just drop duplicates if any
result = result.drop_duplicates()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)