import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_50/training_0.csv", index_col=0)

# Convert numeric columns, fill NaN with 0 for deaths and years
df0['SideADeaths'] = pd.to_numeric(df0['SideADeaths'], errors='coerce').fillna(0).astype(int)
df0['SideBDeaths'] = pd.to_numeric(df0['SideBDeaths'], errors='coerce').fillna(0).astype(int)
df0['StartYear1'] = pd.to_numeric(df0['StartYear1'], errors='coerce').fillna(0).astype(int)
df0['EndYear1'] = pd.to_numeric(df0['EndYear1'], errors='coerce').fillna(0).astype(int)
df0['StartMonth1'] = pd.to_numeric(df0['StartMonth1'], errors='coerce').fillna(0).astype(int)
df0['StartDay1'] = pd.to_numeric(df0['StartDay1'], errors='coerce').fillna(0).astype(int)
df0['EndMonth1'] = pd.to_numeric(df0['EndMonth1'], errors='coerce').fillna(0).astype(int)
df0['EndDay1'] = pd.to_numeric(df0['EndDay1'], errors='coerce').fillna(0).astype(int)
df0['CcodeA'] = pd.to_numeric(df0['CcodeA'], errors='coerce').fillna(0).astype(int)
df0['WarNum'] = pd.to_numeric(df0['WarNum'], errors='coerce').fillna(0).astype(int)
df0['Outcome'] = pd.to_numeric(df0['Outcome'], errors='coerce').fillna(0).astype(int)

# Group by WarNum and CcodeA
agg = df0.groupby(['WarNum', 'CcodeA'], as_index=False).agg({
    'StartMonth1': 'min',
    'StartDay1': 'min',
    'StartYear1': 'min',
    'EndMonth1': 'max',
    'EndDay1': 'max',
    'EndYear1': 'max',
    'SideADeaths': 'sum',
    'SideBDeaths': 'sum',
    'Outcome': 'first',
    'WarName': 'first',
    'Initiator': 'first'
})

# Compute Deaths
agg['Deaths'] = agg['SideADeaths'] + agg['SideBDeaths']

# Encode WarName and Initiator as categorical codes (integers)
agg['PolityName'] = pd.Categorical(agg['WarName']).codes
agg['Initiator'] = pd.Categorical(agg['Initiator']).codes

# Rename columns to target schema
agg.rename(columns={
    'WarNum': 'WarID',
    'CcodeA': 'PolityID',
    'StartMonth1': 'StartMonth',
    'StartDay1': 'StartDay',
    'StartYear1': 'StartYear',
    'EndMonth1': 'EndMonth',
    'EndDay1': 'EndDay',
    'EndYear1': 'EndYear'
}, inplace=True)

# Select and reorder columns as per target schema
agg = agg[['Outcome', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear',
           'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Deaths']]

# Convert all columns to int (already numeric, but ensure no float)
for col in agg.columns:
    agg[col] = pd.to_numeric(agg[col], errors='coerce').fillna(0).astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_50/target_multisource_mcts.csv", index=False)