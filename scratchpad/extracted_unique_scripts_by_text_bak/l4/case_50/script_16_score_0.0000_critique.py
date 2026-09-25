import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_50/training_0.csv", index_col=0)

# Group by Outcome and WarNum (WarID)
df_grouped = df0.groupby(['Outcome', 'WarNum'], as_index=False).agg({
    'CcodeA': 'first',
    'SideA': 'first',
    'StartMonth1': 'first',
    'StartDay1': 'first',
    'StartYear1': 'first',
    'EndMonth1': 'first',
    'EndDay1': 'first',
    'EndYear1': 'first',
    'Initiator': 'first',
    'SideADeaths': 'sum',
    'SideBDeaths': 'sum'
})

# Rename columns to match target schema
df_grouped.rename(columns={
    'WarNum': 'WarID',
    'CcodeA': 'PolityID',
    'SideA': 'PolityName',
    'StartMonth1': 'StartMonth',
    'StartDay1': 'StartDay',
    'StartYear1': 'StartYear',
    'EndMonth1': 'EndMonth',
    'EndDay1': 'EndDay',
    'EndYear1': 'EndYear',
    'Initiator': 'Initiator'
}, inplace=True)

# Combine deaths from both sides
df_grouped['Deaths'] = df_grouped['SideADeaths'].fillna(0) + df_grouped['SideBDeaths'].fillna(0)

# Convert columns to numeric and then to int, filling NaNs with 0
for col in ['Outcome', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear',
            'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Deaths']:
    df_grouped[col] = pd.to_numeric(df_grouped[col], errors='coerce').fillna(0).astype(int)

# Select and order columns as per target schema
df_grouped = df_grouped[['Outcome', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear',
                         'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Deaths']]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_50/target_multisource_mcts.csv", index=False)