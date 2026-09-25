import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_49/training_0.csv", index_col=0)

# Extract SideA data
df_a = df[['WarNum', 'WarName', 'CcodeA', 'SideA', 'StartMonth1', 'StartDay1', 'StartYear1',
           'EndMonth1', 'EndDay1', 'EndYear1', 'Initiator', 'Outcome', 'SideADeaths']].copy()

df_a.columns = ['WarID', 'WarName', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear',
                'EndMonth', 'EndDay', 'EndYear', 'InitiatorName', 'Outcome', 'Deaths']

# Extract SideB data
df_b = df[['WarNum', 'WarName', 'CcodeB', 'SideB', 'StartMonth2', 'StartDay2', 'StartYear2',
           'EndMonth2', 'EndDay2', 'EndYear2', 'Initiator', 'Outcome', 'SideBDeaths']].copy()

df_b.columns = ['WarID', 'WarName', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear',
                'EndMonth', 'EndDay', 'EndYear', 'InitiatorName', 'Outcome', 'Deaths']

# Concatenate SideA and SideB
df_all = pd.concat([df_a, df_b], ignore_index=True)

# Convert types
df_all['PolityName'] = df_all['PolityName'].astype(str)
df_all['InitiatorName'] = df_all['InitiatorName'].astype(str)

df_all['WarID'] = pd.to_numeric(df_all['WarID'], errors='coerce').astype('Int64')
df_all['PolityID'] = pd.to_numeric(df_all['PolityID'], errors='coerce').astype('Int64')

# Dates: fillna with 0 and convert to int
for col in ['StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear']:
    df_all[col] = pd.to_numeric(df_all[col], errors='coerce').fillna(0).astype(int)

# Deaths: fillna with 0 and convert to int
df_all['Deaths'] = pd.to_numeric(df_all['Deaths'], errors='coerce').fillna(0).astype(int)

# Outcome: convert to int, coercing errors to NA
df_all['Outcome'] = pd.to_numeric(df_all['Outcome'], errors='coerce').astype('Int64')

# Create a mapping from (WarID, PolityName) to PolityID to map InitiatorName to Initiator PolityID
# We assume that InitiatorName matches PolityName in the same war
initiator_map = df_all[['WarID', 'PolityName', 'PolityID']].drop_duplicates()

# Merge to get Initiator PolityID
df_all = df_all.merge(initiator_map, how='left',
                      left_on=['WarID', 'InitiatorName'],
                      right_on=['WarID', 'PolityName'],
                      suffixes=('', '_Initiator'))

# Rename Initiator PolityID column
df_all['Initiator'] = df_all['PolityID_Initiator'].astype('Int64')

# Drop helper columns
df_all = df_all.drop(columns=['WarName', 'InitiatorName', 'PolityName_Initiator', 'PolityID_Initiator'])

# Reorder columns to match target schema
df_all = df_all[['PolityName', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear',
                 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']]

# Group by all key columns except Deaths, sum Deaths to remove duplicates
group_cols = ['PolityName', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear',
              'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome']

df_final = df_all.groupby(group_cols, dropna=False, as_index=False).agg({'Deaths': 'sum'})

# Write output
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_49/target_multisource_mcts.csv", index=False)