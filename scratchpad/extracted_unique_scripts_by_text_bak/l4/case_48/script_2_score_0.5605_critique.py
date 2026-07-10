import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_48/training_0.csv", index_col=0)

# Prepare side A
df_a = df[['WarNum', 'Initiator', 'CcodeA', 'StartMonth1', 'StartDay1', 'StartYear1', 'EndMonth1', 'EndDay1', 'EndYear1', 'Outcome', 'SideADeaths']].copy()
df_a = df_a.rename(columns={
    'WarNum': 'WarID',
    'CcodeA': 'PolityID',
    'StartMonth1': 'StartMonth',
    'StartDay1': 'StartDay',
    'StartYear1': 'StartYear',
    'EndMonth1': 'EndMonth',
    'EndDay1': 'EndDay',
    'EndYear1': 'EndYear',
    'SideADeaths': 'Deaths'
})

# Prepare side B
df_b = df[['WarNum', 'Initiator', 'CcodeB', 'StartMonth2', 'StartDay2', 'StartYear2', 'EndMonth2', 'EndDay2', 'EndYear2', 'Outcome', 'SideBDeaths']].copy()
df_b = df_b.rename(columns={
    'WarNum': 'WarID',
    'CcodeB': 'PolityID',
    'StartMonth2': 'StartMonth',
    'StartDay2': 'StartDay',
    'StartYear2': 'StartYear',
    'EndMonth2': 'EndMonth',
    'EndDay2': 'EndDay',
    'EndYear2': 'EndYear',
    'SideBDeaths': 'Deaths'
})

# Concatenate both sides (UNION)
df_all = pd.concat([df_a, df_b], ignore_index=True)

# Drop rows with missing PolityID or StartYear (minimal date info)
df_all = df_all.dropna(subset=['PolityID', 'StartYear'])

# Cast columns to correct types
df_all['WarID'] = df_all['WarID'].astype(int)
df_all['PolityID'] = df_all['PolityID'].astype(int)
# PolityName is integer in target, assign PolityName = PolityID (no other integer polity name column)
df_all['PolityName'] = df_all['PolityID']
df_all['StartMonth'] = df_all['StartMonth'].fillna(0).astype(int)
df_all['StartDay'] = df_all['StartDay'].fillna(0).astype(int)
df_all['StartYear'] = df_all['StartYear'].astype(int)
df_all['EndMonth'] = df_all['EndMonth'].fillna(0).astype(int)
df_all['EndDay'] = df_all['EndDay'].fillna(0).astype(int)
df_all['EndYear'] = df_all['EndYear'].fillna(0).astype(int)
df_all['Outcome'] = df_all['Outcome'].astype(int)
df_all['Deaths'] = df_all['Deaths'].fillna(0).astype(int)
df_all['Initiator'] = df_all['Initiator'].astype(str)

# Group by key columns and sum Deaths
group_cols = ['Initiator', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear',
              'EndMonth', 'EndDay', 'EndYear', 'Outcome']

result = df_all.groupby(group_cols, as_index=False).agg({'Deaths': 'sum'})

# Reorder columns to match target schema exactly
result = result[['Initiator', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear',
                 'EndMonth', 'EndDay', 'EndYear', 'Outcome', 'Deaths']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_48/target_multisource_mcts.csv", index=False)