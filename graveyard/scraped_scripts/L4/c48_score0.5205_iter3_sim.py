import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_48/training_0.csv", index_col=0)

df0['WarID'] = df0['WarNum'].astype('Int64')
df0['PolityID'] = df0['CcodeA'].astype('Int64')
df0['PolityName'] = df0['CcodeA'].astype('Int64')

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

df0['StartMonth'] = df0.apply(choose_start_month, axis=1)
df0['StartDay'] = df0.apply(choose_start_day, axis=1)
df0['StartYear'] = df0.apply(choose_start_year, axis=1)
df0['EndMonth'] = df0.apply(choose_end_month, axis=1)
df0['EndDay'] = df0.apply(choose_end_day, axis=1)
df0['EndYear'] = df0.apply(choose_end_year, axis=1)

df0['Outcome'] = df0['Outcome'].astype('Int64')

df0['SideADeaths'] = pd.to_numeric(df0['SideADeaths'], errors='coerce').fillna(0).astype('Int64')
df0['SideBDeaths'] = pd.to_numeric(df0['SideBDeaths'], errors='coerce').fillna(0).astype('Int64')
df0['Deaths'] = df0['SideADeaths'] + df0['SideBDeaths']

result = df0[['Initiator', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Outcome', 'Deaths']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_48/target_multisource_mcts.csv", index=False)