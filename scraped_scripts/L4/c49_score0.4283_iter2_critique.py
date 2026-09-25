import pandas as pd

# Read source table
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_49/training_0.csv", index_col=0)

# Convert numeric columns, fill deaths NaN with 0
df0['SideADeaths'] = pd.to_numeric(df0['SideADeaths'], errors='coerce').fillna(0).astype('Int64')
df0['SideBDeaths'] = pd.to_numeric(df0['SideBDeaths'], errors='coerce').fillna(0).astype('Int64')

# Convert date columns to Int64 (allow NaN)
for col in ['StartMonth1', 'StartDay1', 'StartYear1', 'EndMonth1', 'EndDay1', 'EndYear1']:
    df0[col] = pd.to_numeric(df0[col], errors='coerce').astype('Int64')

# Convert Initiator and Outcome to Int64 (may have NaN)
df0['Initiator'] = pd.to_numeric(df0['Initiator'], errors='coerce').astype('Int64')
df0['Outcome'] = pd.to_numeric(df0['Outcome'], errors='coerce').astype('Int64')

# Prepare SideA dataframe
sidea = pd.DataFrame({
    'PolityName': df0['SideA'].astype(str),
    'WarID': df0['WarNum'].astype('Int64'),
    'PolityID': pd.to_numeric(df0['CcodeA'], errors='coerce').astype('Int64'),
    'StartMonth': df0['StartMonth1'],
    'StartDay': df0['StartDay1'],
    'StartYear': df0['StartYear1'],
    'EndMonth': df0['EndMonth1'],
    'EndDay': df0['EndDay1'],
    'EndYear': df0['EndYear1'],
    'Initiator': df0['Initiator'],
    'Outcome': df0['Outcome'],
    'Deaths': df0['SideADeaths']
})

# Prepare SideB dataframe
sideb = pd.DataFrame({
    'PolityName': df0['SideB'].astype(str),
    'WarID': df0['WarNum'].astype('Int64'),
    'PolityID': pd.to_numeric(df0['CcodeB'], errors='coerce').astype('Int64'),
    'StartMonth': df0['StartMonth1'],
    'StartDay': df0['StartDay1'],
    'StartYear': df0['StartYear1'],
    'EndMonth': df0['EndMonth1'],
    'EndDay': df0['EndDay1'],
    'EndYear': df0['EndYear1'],
    'Initiator': df0['Initiator'],
    'Outcome': df0['Outcome'],
    'Deaths': df0['SideBDeaths']
})

# Combine SideA and SideB dataframes (UNION)
combined = pd.concat([sidea, sideb], ignore_index=True)

# Remove rows where PolityName is 'nan' or PolityID is NaN (no polity info)
combined = combined[combined['PolityName'].notna()]
combined = combined[combined['PolityID'].notna()]

# Group by all columns except Deaths, sum Deaths
group_cols = ['PolityName', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear',
              'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome']

result = combined.groupby(group_cols, dropna=False, as_index=False).agg({'Deaths': 'sum'})

# Convert Deaths to Int64
result['Deaths'] = result['Deaths'].astype('Int64')

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_49/target_multisource_mcts.csv", index=False)