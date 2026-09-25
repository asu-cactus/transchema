import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_50/training_0.csv", index_col=0)

# Prepare SideA dataframe
sideA = pd.DataFrame({
    'Outcome': pd.to_numeric(df0['Outcome'], errors='coerce'),
    'WarNum': pd.to_numeric(df0['WarNum'], errors='coerce'),
    'PolityID': pd.to_numeric(df0['CcodeA'], errors='coerce'),
    'PolityName': df0['SideA'],
    'StartMonth': pd.to_numeric(df0['StartMonth1'], errors='coerce'),
    'StartDay': pd.to_numeric(df0['StartDay1'], errors='coerce'),
    'StartYear': pd.to_numeric(df0['StartYear1'], errors='coerce'),
    'EndMonth': pd.to_numeric(df0['EndMonth1'], errors='coerce'),
    'EndDay': pd.to_numeric(df0['EndDay1'], errors='coerce'),
    'EndYear': pd.to_numeric(df0['EndYear1'], errors='coerce'),
    'Initiator': df0['Initiator'],
    'Deaths': pd.to_numeric(df0['SideADeaths'], errors='coerce').fillna(0)
})

# Prepare SideB dataframe
sideB = pd.DataFrame({
    'Outcome': pd.to_numeric(df0['Outcome'], errors='coerce'),
    'WarNum': pd.to_numeric(df0['WarNum'], errors='coerce'),
    'PolityID': pd.to_numeric(df0['CcodeB'], errors='coerce'),
    'PolityName': df0['SideB'],
    'StartMonth': pd.to_numeric(df0['StartMonth1'], errors='coerce'),
    'StartDay': pd.to_numeric(df0['StartDay1'], errors='coerce'),
    'StartYear': pd.to_numeric(df0['StartYear1'], errors='coerce'),
    'EndMonth': pd.to_numeric(df0['EndMonth1'], errors='coerce'),
    'EndDay': pd.to_numeric(df0['EndDay1'], errors='coerce'),
    'EndYear': pd.to_numeric(df0['EndYear1'], errors='coerce'),
    'Initiator': df0['Initiator'],
    'Deaths': pd.to_numeric(df0['SideBDeaths'], errors='coerce').fillna(0)
})

# Concatenate SideA and SideB dataframes (UNION)
df_union = pd.concat([sideA, sideB], ignore_index=True)

# Remove rows where PolityID is NaN (invalid polity)
df_union = df_union.dropna(subset=['PolityID'])

# Group by the leftmost columns of target schema (non-float, unique)
group_cols = ['Outcome', 'WarNum', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator']

result = df_union.groupby(group_cols, dropna=False, as_index=False).agg({'Deaths': 'sum'})

# Rename columns to match target schema
result = result.rename(columns={
    'WarNum': 'WarID'
})

# Convert all columns to int as per target schema
for col in ['Outcome', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Deaths']:
    result[col] = pd.to_numeric(result[col], errors='coerce').fillna(0).astype(int)

# PolityName is string in source but target schema says integer, so convert PolityName to integer by encoding strings
# Since target examples show PolityName as integer, we encode unique polity names as integers
result['PolityName'] = pd.factorize(result['PolityName'])[0].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_50/target_multisource_mcts.csv", index=False)