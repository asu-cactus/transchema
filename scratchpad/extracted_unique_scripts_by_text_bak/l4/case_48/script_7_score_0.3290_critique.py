import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_48/training_0.csv", index_col=0)

# Prepare SideA dataframe
sideA_df = df[['WarNum', 'Initiator', 'Outcome', 'CcodeA', 'SideA', 'StartMonth1', 'StartDay1', 'StartYear1',
               'EndMonth1', 'EndDay1', 'EndYear1', 'SideADeaths']].copy()

# Rename columns to target schema
sideA_df = sideA_df.rename(columns={
    'WarNum': 'WarID',
    'CcodeA': 'PolityID',
    'SideA': 'PolityName',  # PolityName is integer, so we will convert below
    'StartMonth1': 'StartMonth',
    'StartDay1': 'StartDay',
    'StartYear1': 'StartYear',
    'EndMonth1': 'EndMonth',
    'EndDay1': 'EndDay',
    'EndYear1': 'EndYear',
    'SideADeaths': 'Deaths'
})

# Filter rows where Initiator matches SideA (string match)
sideA_df = sideA_df[sideA_df['Initiator'] == sideA_df['PolityName']]

# PolityName must be integer, but SideA is string, so convert PolityName to PolityID integer
# Since PolityName is string, but target expects integer, we set PolityName = PolityID (int)
sideA_df['PolityName'] = sideA_df['PolityID']

# Prepare SideB dataframe
sideB_df = df[['WarNum', 'Initiator', 'Outcome', 'CcodeB', 'SideB', 'StartMonth1', 'StartDay1', 'StartYear1',
               'EndMonth1', 'EndDay1', 'EndYear1', 'SideBDeaths']].copy()

sideB_df = sideB_df.rename(columns={
    'WarNum': 'WarID',
    'CcodeB': 'PolityID',
    'SideB': 'PolityName',
    'StartMonth1': 'StartMonth',
    'StartDay1': 'StartDay',
    'StartYear1': 'StartYear',
    'EndMonth1': 'EndMonth',
    'EndDay1': 'EndDay',
    'EndYear1': 'EndYear',
    'SideBDeaths': 'Deaths'
})

sideB_df = sideB_df[sideB_df['Initiator'] == sideB_df['PolityName']]

sideB_df['PolityName'] = sideB_df['PolityID']

# Concatenate both sides
combined_df = pd.concat([sideA_df, sideB_df], ignore_index=True)

# Drop rows with NaN PolityID or Initiator (to avoid invalid rows)
combined_df = combined_df.dropna(subset=['PolityID', 'Initiator'])

# Convert columns to correct types
combined_df['WarID'] = combined_df['WarID'].astype(int)
combined_df['PolityID'] = combined_df['PolityID'].astype(int)
combined_df['PolityName'] = combined_df['PolityName'].astype(int)
combined_df['Outcome'] = combined_df['Outcome'].astype(int)

# For date columns, convert to Int64 (nullable integer) to keep NaNs if any
date_cols = ['StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear']
for col in date_cols:
    combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce').astype('Int64')

# Deaths: convert to int, fill NaN with 0
combined_df['Deaths'] = pd.to_numeric(combined_df['Deaths'], errors='coerce').fillna(0).astype(int)

# Group by keys and aggregate
agg_dict = {
    'StartMonth': 'first',
    'StartDay': 'first',
    'StartYear': 'first',
    'EndMonth': 'first',
    'EndDay': 'first',
    'EndYear': 'first',
    'Deaths': 'sum'
}

result_df = combined_df.groupby(['Initiator', 'WarID', 'PolityID', 'Outcome'], as_index=False).agg(agg_dict)

# PolityName = PolityID (integer)
result_df['PolityName'] = result_df['PolityID']

# Reorder columns to match target schema exactly
result_df = result_df[['Initiator', 'WarID', 'PolityID', 'PolityName',
                       'StartMonth', 'StartDay', 'StartYear',
                       'EndMonth', 'EndDay', 'EndYear',
                       'Outcome', 'Deaths']]

result_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_48/target_multisource_mcts.csv", index=False)