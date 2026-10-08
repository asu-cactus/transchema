import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_50/training_0.csv", index_col=0)

# Convert columns to appropriate types
df0['Outcome'] = pd.to_numeric(df0['Outcome'], errors='coerce').astype('Int64')
df0['WarNum'] = pd.to_numeric(df0['WarNum'], errors='coerce').astype('Int64')
df0['CcodeA'] = pd.to_numeric(df0['CcodeA'], errors='coerce').astype('Int64')
df0['Initiator'] = pd.to_numeric(df0['Initiator'], errors='coerce').astype('Int64')

# Death columns: fill NaN with 0 before sum
df0['SideADeaths'] = pd.to_numeric(df0['SideADeaths'], errors='coerce').fillna(0).astype(int)
df0['SideBDeaths'] = pd.to_numeric(df0['SideBDeaths'], errors='coerce').fillna(0).astype(int)

# Group by keys
group_keys = ['Outcome', 'WarNum', 'CcodeA', 'Initiator']

df_grouped = df0.groupby(group_keys, dropna=False, as_index=False).agg({
    'SideADeaths': 'sum',
    'SideBDeaths': 'sum',
    'StartMonth1': 'first',
    'StartDay1': 'first',
    'StartYear1': 'first',
    'EndMonth1': 'first',
    'EndDay1': 'first',
    'EndYear1': 'first'
})

# Calculate Deaths
df_grouped['Deaths'] = df_grouped['SideADeaths'] + df_grouped['SideBDeaths']

# Rename columns to target schema
df_grouped.rename(columns={
    'WarNum': 'WarID',
    'CcodeA': 'PolityID',
    'StartMonth1': 'StartMonth',
    'StartDay1': 'StartDay',
    'StartYear1': 'StartYear',
    'EndMonth1': 'EndMonth',
    'EndDay1': 'EndDay',
    'EndYear1': 'EndYear',
}, inplace=True)

# PolityName = PolityID
df_grouped['PolityName'] = df_grouped['PolityID']

# Select and reorder columns as per target schema
df_final = df_grouped[['Outcome', 'WarID', 'PolityID', 'PolityName',
                       'StartMonth', 'StartDay', 'StartYear',
                       'EndMonth', 'EndDay', 'EndYear',
                       'Initiator', 'Deaths']]

# Cast all columns to Int64 (nullable integer)
df_final = df_final.astype({
    'Outcome': 'Int64',
    'WarID': 'Int64',
    'PolityID': 'Int64',
    'PolityName': 'Int64',
    'StartMonth': 'Int64',
    'StartDay': 'Int64',
    'StartYear': 'Int64',
    'EndMonth': 'Int64',
    'EndDay': 'Int64',
    'EndYear': 'Int64',
    'Initiator': 'Int64',
    'Deaths': 'Int64'
})

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_50/target_multisource_mcts.csv", index=False)