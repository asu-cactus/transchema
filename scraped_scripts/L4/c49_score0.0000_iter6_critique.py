import pandas as pd

# Read source table
df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_49/training_0.csv", index_col=0)

# Clean numeric columns
df['SideADeaths'] = pd.to_numeric(df['SideADeaths'].astype(str).str.replace(',', ''), errors='coerce').fillna(0).astype(int)
df['SideBDeaths'] = pd.to_numeric(df['SideBDeaths'].astype(str).str.replace(',', ''), errors='coerce').fillna(0).astype(int)
df['WarNum'] = pd.to_numeric(df['WarNum'], errors='coerce').fillna(0).astype(int)
df['CcodeA'] = pd.to_numeric(df['CcodeA'], errors='coerce').fillna(0).astype(int)
df['CcodeB'] = pd.to_numeric(df['CcodeB'], errors='coerce').fillna(0).astype(int)

# Convert Initiator and Outcome to numeric if possible, else NaN
df['Initiator'] = pd.to_numeric(df['Initiator'], errors='coerce')
df['Outcome'] = pd.to_numeric(df['Outcome'], errors='coerce')

# Prepare SideA dataframe
sideA = pd.DataFrame({
    'PolityName': df['SideA'],
    'WarID': df['WarNum'],
    'PolityID': df['CcodeA'],
    'StartMonth': pd.to_numeric(df['StartMonth1'], errors='coerce').fillna(0).astype(int),
    'StartDay': pd.to_numeric(df['StartDay1'], errors='coerce').fillna(0).astype(int),
    'StartYear': pd.to_numeric(df['StartYear1'], errors='coerce').fillna(0).astype(int),
    'EndMonth': pd.to_numeric(df['EndMonth1'], errors='coerce').fillna(0).astype(int),
    'EndDay': pd.to_numeric(df['EndDay1'], errors='coerce').fillna(0).astype(int),
    'EndYear': pd.to_numeric(df['EndYear1'], errors='coerce').fillna(0).astype(int),
    'Initiator': df['Initiator'],
    'Outcome': df['Outcome'],
    'Deaths': df['SideADeaths']
})

# Prepare SideB dataframe
sideB = pd.DataFrame({
    'PolityName': df['SideB'],
    'WarID': df['WarNum'],
    'PolityID': df['CcodeB'],
    'StartMonth': pd.to_numeric(df['StartMonth1'], errors='coerce').fillna(0).astype(int),
    'StartDay': pd.to_numeric(df['StartDay1'], errors='coerce').fillna(0).astype(int),
    'StartYear': pd.to_numeric(df['StartYear1'], errors='coerce').fillna(0).astype(int),
    'EndMonth': pd.to_numeric(df['EndMonth1'], errors='coerce').fillna(0).astype(int),
    'EndDay': pd.to_numeric(df['EndDay1'], errors='coerce').fillna(0).astype(int),
    'EndYear': pd.to_numeric(df['EndYear1'], errors='coerce').fillna(0).astype(int),
    'Initiator': df['Initiator'],
    'Outcome': df['Outcome'],
    'Deaths': df['SideBDeaths']
})

# Concatenate SideA and SideB dataframes (UNION)
union_df = pd.concat([sideA, sideB], ignore_index=True)

# Remove rows where PolityName is NaN or PolityID is 0 (invalid polity)
union_df = union_df[union_df['PolityName'].notna()]
union_df = union_df[union_df['PolityID'] != 0]

# Group by all columns except Deaths, sum Deaths
group_cols = ['PolityName', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear',
              'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome']

result = union_df.groupby(group_cols, as_index=False).agg({'Deaths': 'sum'})

# Convert columns to correct types
result['PolityName'] = result['PolityName'].astype(str)
result['WarID'] = result['WarID'].astype(int)
result['PolityID'] = result['PolityID'].astype(int)
result['StartMonth'] = result['StartMonth'].astype(int)
result['StartDay'] = result['StartDay'].astype(int)
result['StartYear'] = result['StartYear'].astype(int)
result['EndMonth'] = result['EndMonth'].astype(int)
result['EndDay'] = result['EndDay'].astype(int)
result['EndYear'] = result['EndYear'].astype(int)
# Initiator and Outcome may have NaNs, fill with 0 and convert to int
result['Initiator'] = result['Initiator'].fillna(0).astype(int)
result['Outcome'] = result['Outcome'].fillna(0).astype(int)
result['Deaths'] = result['Deaths'].astype(int)

# Reorder columns to match target schema
final_cols = ['PolityName', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear',
              'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']

result = result[final_cols]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_49/target_multisource_mcts.csv", index=False)