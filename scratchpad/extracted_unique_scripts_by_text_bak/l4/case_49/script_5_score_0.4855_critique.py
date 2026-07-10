import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_49/training_0.csv", index_col=0)

# Extract side A data
df_a = df[['WarNum', 'WarName', 'WarType', 'CcodeA', 'SideA', 'StartMonth1', 'StartDay1', 'StartYear1',
           'EndMonth1', 'EndDay1', 'EndYear1', 'SideADeaths', 'Initiator', 'Outcome']].copy()
df_a.columns = ['WarID', 'WarName', 'WarType', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear',
                'EndMonth', 'EndDay', 'EndYear', 'Deaths', 'Initiator', 'Outcome']

# Extract side B data
df_b = df[['WarNum', 'WarName', 'WarType', 'CcodeB', 'SideB', 'StartMonth2', 'StartDay2', 'StartYear2',
           'EndMonth2', 'EndDay2', 'EndYear2', 'SideBDeaths', 'Initiator', 'Outcome']].copy()
df_b.columns = ['WarID', 'WarName', 'WarType', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear',
                'EndMonth', 'EndDay', 'EndYear', 'Deaths', 'Initiator', 'Outcome']

# Convert PolityID to int, fill NaN with 0
df_a['PolityID'] = pd.to_numeric(df_a['PolityID'], errors='coerce').fillna(0).astype(int)
df_b['PolityID'] = pd.to_numeric(df_b['PolityID'], errors='coerce').fillna(0).astype(int)

# Convert other columns to int, fill NaN with 0
for col in ['StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Deaths', 'Initiator', 'Outcome']:
    df_a[col] = pd.to_numeric(df_a[col], errors='coerce').fillna(0).astype(int)
    df_b[col] = pd.to_numeric(df_b[col], errors='coerce').fillna(0).astype(int)

# Concatenate side A and side B data (UNION)
df_union = pd.concat([df_a, df_b], ignore_index=True)

# Group by all key columns except Deaths, sum Deaths
group_cols = ['PolityName', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear',
              'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome']

df_result = df_union.groupby(group_cols, dropna=False, as_index=False).agg({'Deaths': 'sum'})

# Ensure columns order as target schema
df_result = df_result[['PolityName', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear',
                       'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length4_49/target_multisource_mcts.csv", index=False)