import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_49/training_0.csv", index_col=0)

def extract_polity_rows(df, side_prefix, polity_col, side_col, deaths_col):
    df_side = df[[ 'WarNum', polity_col, side_col,
                   f'StartMonth{side_prefix}', f'StartDay{side_prefix}', f'StartYear{side_prefix}',
                   f'EndMonth{side_prefix}', f'EndDay{side_prefix}', f'EndYear{side_prefix}',
                   'Initiator', 'Outcome', deaths_col]].copy()
    df_side = df_side.rename(columns={
        'WarNum': 'WarID',
        polity_col: 'PolityID',
        side_col: 'PolityName',
        f'StartMonth{side_prefix}': 'StartMonth',
        f'StartDay{side_prefix}': 'StartDay',
        f'StartYear{side_prefix}': 'StartYear',
        f'EndMonth{side_prefix}': 'EndMonth',
        f'EndDay{side_prefix}': 'EndDay',
        f'EndYear{side_prefix}': 'EndYear',
        deaths_col: 'Deaths'
    })
    return df_side

sideA = extract_polity_rows(df0, '1', 'CcodeA', 'SideA', 'SideADeaths')
sideB = extract_polity_rows(df0, '1', 'CcodeB', 'SideB', 'SideBDeaths')

sideA['PolityName'] = sideA['PolityName'].astype(str)
sideB['PolityName'] = sideB['PolityName'].astype(str)

df = pd.concat([sideA, sideB], ignore_index=True)

df['PolityID'] = pd.to_numeric(df['PolityID'], errors='coerce').fillna(0).astype(int)
df['WarID'] = pd.to_numeric(df['WarID'], errors='coerce').fillna(0).astype(int)
df['StartMonth'] = pd.to_numeric(df['StartMonth'], errors='coerce').fillna(1).astype(int)
df['StartDay'] = pd.to_numeric(df['StartDay'], errors='coerce').fillna(1).astype(int)
df['StartYear'] = pd.to_numeric(df['StartYear'], errors='coerce').fillna(1).astype(int)
df['EndMonth'] = pd.to_numeric(df['EndMonth'], errors='coerce').fillna(1).astype(int)
df['EndDay'] = pd.to_numeric(df['EndDay'], errors='coerce').fillna(1).astype(int)
df['EndYear'] = pd.to_numeric(df['EndYear'], errors='coerce').fillna(1).astype(int)
df['Initiator'] = pd.to_numeric(df['Initiator'], errors='coerce').fillna(0).astype(int)
df['Outcome'] = pd.to_numeric(df['Outcome'], errors='coerce').fillna(0).astype(int)
df['Deaths'] = pd.to_numeric(df['Deaths'], errors='coerce').fillna(0).astype(int)

# Group by PolityName, WarID, PolityID and aggregate
agg_dict = {
    'Deaths': 'sum',
    'StartMonth': 'first',
    'StartDay': 'first',
    'StartYear': 'first',
    'EndMonth': 'first',
    'EndDay': 'first',
    'EndYear': 'first',
    'Initiator': 'first',
    'Outcome': 'first'
}

df = df.groupby(['PolityName', 'WarID', 'PolityID'], as_index=False).agg(agg_dict)

df = df[['PolityName', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear',
         'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_49/target_multisource_mcts.csv", index=False)