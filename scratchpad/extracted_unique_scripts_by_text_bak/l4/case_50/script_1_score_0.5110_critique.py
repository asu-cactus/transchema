import pandas as pd

# Read source data
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_50/training_0.csv", index_col=0)

# Prepare side A dataframe
dfA = df0[['WarNum', 'CcodeA', 'SideA', 'StartMonth1', 'StartDay1', 'StartYear1',
           'EndMonth1', 'EndDay1', 'EndYear1', 'Initiator', 'Outcome', 'SideADeaths']].copy()
dfA.columns = ['WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear',
               'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']

# Prepare side B dataframe
dfB = df0[['WarNum', 'CcodeB', 'SideB', 'StartMonth2', 'StartDay2', 'StartYear2',
           'EndMonth2', 'EndDay2', 'EndYear2', 'Initiator', 'Outcome', 'SideBDeaths']].copy()
dfB.columns = ['WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear',
               'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']

# Keep all rows, do not drop rows with missing PolityID or PolityName
# Convert all columns to appropriate types, fill NaNs in numeric columns with 0
for col in ['WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear',
            'EndMonth', 'EndDay', 'EndYear', 'Outcome', 'Deaths']:
    dfA[col] = pd.to_numeric(dfA[col], errors='coerce').fillna(0).astype(int)
    dfB[col] = pd.to_numeric(dfB[col], errors='coerce').fillna(0).astype(int)

# Convert PolityName (string) to integer codes consistently across both dfs
# Combine PolityName columns from both dfs to get consistent mapping
all_polity_names = pd.concat([dfA['PolityName'], dfB['PolityName']], ignore_index=True)
# Factorize to get integer codes, starting from 1 to avoid confusion with 0 as missing
polity_name_codes, uniques = pd.factorize(all_polity_names)
# Map back to dfs
dfA['PolityName'] = polity_name_codes[:len(dfA)] + 1
dfB['PolityName'] = polity_name_codes[len(dfA):] + 1

# Similarly convert Initiator (string) to integer codes consistently
all_initiators = pd.concat([dfA['Initiator'], dfB['Initiator']], ignore_index=True)
initiator_codes, initiator_uniques = pd.factorize(all_initiators)
dfA['Initiator'] = initiator_codes[:len(dfA)] + 1
dfB['Initiator'] = initiator_codes[len(dfA):] + 1

# Concatenate side A and side B dataframes (UNION)
df = pd.concat([dfA, dfB], ignore_index=True)

# Group by the leftmost columns of target schema except Deaths (which is aggregated)
group_by_cols = ['Outcome', 'WarID', 'PolityID', 'PolityName',
                 'StartMonth', 'StartDay', 'StartYear',
                 'EndMonth', 'EndDay', 'EndYear', 'Initiator']

df_grouped = df.groupby(group_by_cols, dropna=False, as_index=False).agg({'Deaths': 'sum'})

# Ensure all columns are int type as per target schema
for col in df_grouped.columns:
    df_grouped[col] = pd.to_numeric(df_grouped[col], errors='coerce').fillna(0).astype(int)

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_50/target_multisource_mcts.csv", index=False)