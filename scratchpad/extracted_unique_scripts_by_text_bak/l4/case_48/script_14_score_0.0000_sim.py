import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_48/training_0.csv", index_col=0)

df_join = pd.merge(df0, df0, left_on=['WarNum', 'CcodeA'], right_on=['WarNum', 'CcodeB'], suffixes=('_A', '_B'))

df_join['Deaths'] = df_join[['SideADeaths_A', 'SideBDeaths_B']].fillna(0).sum(axis=1)

df_join['PolityID'] = df_join['CcodeA']
df_join['PolityName'] = df_join['CcodeB']

def choose_start_month(row):
    if pd.notna(row['StartMonth1']):
        return int(row['StartMonth1'])
    elif pd.notna(row['StartMonth2']):
        return int(row['StartMonth2'])
    else:
        return pd.NA

def choose_start_day(row):
    if pd.notna(row['StartDay1']):
        return int(row['StartDay1'])
    elif pd.notna(row['StartDay2']):
        return int(row['StartDay2'])
    else:
        return pd.NA

def choose_start_year(row):
    if pd.notna(row['StartYear1']):
        return int(row['StartYear1'])
    elif pd.notna(row['StartYear2']):
        return int(row['StartYear2'])
    else:
        return pd.NA

def choose_end_month(row):
    if pd.notna(row['EndMonth1']):
        return int(row['EndMonth1'])
    elif pd.notna(row['EndMonth2']):
        return int(row['EndMonth2'])
    else:
        return pd.NA

def choose_end_day(row):
    if pd.notna(row['EndDay1']):
        return int(row['EndDay1'])
    elif pd.notna(row['EndDay2']):
        return int(row['EndDay2'])
    else:
        return pd.NA

def choose_end_year(row):
    if pd.notna(row['EndYear1']):
        return int(row['EndYear1'])
    elif pd.notna(row['EndYear2']):
        return int(row['EndYear2'])
    else:
        return pd.NA

df_join['StartMonth'] = df_join.apply(choose_start_month, axis=1)
df_join['StartDay'] = df_join.apply(choose_start_day, axis=1)
df_join['StartYear'] = df_join.apply(choose_start_year, axis=1)
df_join['EndMonth'] = df_join.apply(choose_end_month, axis=1)
df_join['EndDay'] = df_join.apply(choose_end_day, axis=1)
df_join['EndYear'] = df_join.apply(choose_end_year, axis=1)

df_result = df_join.groupby('Initiator').agg({
    'WarNum': 'first',
    'PolityID': 'first',
    'PolityName': 'first',
    'StartMonth': 'first',
    'StartDay': 'first',
    'StartYear': 'first',
    'EndMonth': 'first',
    'EndDay': 'first',
    'EndYear': 'first',
    'Outcome': 'first',
    'Deaths': 'sum'
}).reset_index()

df_result.rename(columns={
    'WarNum': 'WarID'
}, inplace=True)

df_result = df_result[['Initiator', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Outcome', 'Deaths']]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length4_48/target_multisource_mcts.csv", index=False)