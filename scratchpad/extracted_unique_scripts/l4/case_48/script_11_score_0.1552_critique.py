import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_48/training_0.csv", index_col=0)

# Prepare side A data
df_a = df0[['WarNum', 'Initiator', 'Outcome', 'SideADeaths', 'CcodeA', 'SideA',
            'StartMonth1', 'StartDay1', 'StartYear1', 'EndMonth1', 'EndDay1', 'EndYear1']].copy()
df_a.rename(columns={
    'WarNum': 'WarID',
    'CcodeA': 'PolityID',
    'SideA': 'PolityName',
    'StartMonth1': 'StartMonth',
    'StartDay1': 'StartDay',
    'StartYear1': 'StartYear',
    'EndMonth1': 'EndMonth',
    'EndDay1': 'EndDay',
    'EndYear1': 'EndYear',
    'SideADeaths': 'Deaths'
}, inplace=True)

# Prepare side B data
df_b = df0[['WarNum', 'Initiator', 'Outcome', 'SideBDeaths', 'CcodeB', 'SideB',
            'StartMonth2', 'StartDay2', 'StartYear2', 'EndMonth2', 'EndDay2', 'EndYear2']].copy()
df_b.rename(columns={
    'WarNum': 'WarID',
    'CcodeB': 'PolityID',
    'SideB': 'PolityName',
    'StartMonth2': 'StartMonth',
    'StartDay2': 'StartDay',
    'StartYear2': 'StartYear',
    'EndMonth2': 'EndMonth',
    'EndDay2': 'EndDay',
    'EndYear2': 'EndYear',
    'SideBDeaths': 'Deaths'
}, inplace=True)

# Convert types for both dataframes
for df in [df_a, df_b]:
    df['Initiator'] = df['Initiator'].astype(str)
    df['WarID'] = pd.to_numeric(df['WarID'], errors='coerce').astype('Int64')
    df['PolityID'] = pd.to_numeric(df['PolityID'], errors='coerce').astype('Int64')
    df['PolityName'] = pd.to_numeric(df['PolityName'], errors='coerce').astype('Int64')
    df['StartMonth'] = pd.to_numeric(df['StartMonth'], errors='coerce').astype('Int64')
    df['StartDay'] = pd.to_numeric(df['StartDay'], errors='coerce').astype('Int64')
    df['StartYear'] = pd.to_numeric(df['StartYear'], errors='coerce').astype('Int64')
    df['EndMonth'] = pd.to_numeric(df['EndMonth'], errors='coerce').astype('Int64')
    df['EndDay'] = pd.to_numeric(df['EndDay'], errors='coerce').astype('Int64')
    df['EndYear'] = pd.to_numeric(df['EndYear'], errors='coerce').astype('Int64')
    df['Outcome'] = pd.to_numeric(df['Outcome'], errors='coerce').astype('Int64')
    df['Deaths'] = pd.to_numeric(df['Deaths'], errors='coerce').fillna(0).astype('Int64')

# UNION the two dataframes
df_union = pd.concat([df_a, df_b], ignore_index=True)

# GROUP BY the key columns and sum Deaths
group_by_cols = ['Initiator', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear',
                 'EndMonth', 'EndDay', 'EndYear', 'Outcome']

df_final = df_union.groupby(group_by_cols, dropna=False, as_index=False).agg({'Deaths': 'sum'})

# Ensure column order matches target schema
df_final = df_final[['Initiator', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear',
                     'EndMonth', 'EndDay', 'EndYear', 'Outcome', 'Deaths']]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_48/target_multisource_mcts.csv", index=False)