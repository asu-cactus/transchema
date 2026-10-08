import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_48/training_0.csv", index_col=0)

df = df0.copy()

df['PolityID'] = df['CcodeA'].fillna(df['CcodeB'])
df['PolityName'] = df['CcodeA'].fillna(df['CcodeB'])

def to_int_safe(x):
    try:
        if pd.isna(x):
            return pd.NA
        if isinstance(x, str):
            return int(x.replace(',', ''))
        return int(x)
    except:
        return pd.NA

for col in ['PolityID', 'PolityName']:
    df[col] = df[col].apply(to_int_safe)

df['WarID'] = df['WarNum'].apply(to_int_safe)

def choose_start_month(row):
    if not pd.isna(row['StartMonth1']):
        return int(row['StartMonth1'])
    elif not pd.isna(row['StartMonth2']):
        return int(row['StartMonth2'])
    else:
        return pd.NA

def choose_start_day(row):
    if not pd.isna(row['StartDay1']):
        return int(row['StartDay1'])
    elif not pd.isna(row['StartDay2']):
        return int(row['StartDay2'])
    else:
        return pd.NA

def choose_start_year(row):
    if not pd.isna(row['StartYear1']):
        return int(row['StartYear1'])
    elif not pd.isna(row['StartYear2']):
        return int(row['StartYear2'])
    else:
        return pd.NA

def choose_end_month(row):
    if not pd.isna(row['EndMonth1']):
        return int(row['EndMonth1'])
    elif not pd.isna(row['EndMonth2']):
        return int(row['EndMonth2'])
    else:
        return pd.NA

def choose_end_day(row):
    if not pd.isna(row['EndDay1']):
        return int(row['EndDay1'])
    elif not pd.isna(row['EndDay2']):
        return int(row['EndDay2'])
    else:
        return pd.NA

def choose_end_year(row):
    if not pd.isna(row['EndYear1']):
        return int(row['EndYear1'])
    elif not pd.isna(row['EndYear2']):
        return int(row['EndYear2'])
    else:
        return pd.NA

df['StartMonth'] = df.apply(choose_start_month, axis=1)
df['StartDay'] = df.apply(choose_start_day, axis=1)
df['StartYear'] = df.apply(choose_start_year, axis=1)
df['EndMonth'] = df.apply(choose_end_month, axis=1)
df['EndDay'] = df.apply(choose_end_day, axis=1)
df['EndYear'] = df.apply(choose_end_year, axis=1)

df['Outcome'] = df['Outcome'].apply(to_int_safe)

df['SideADeaths'] = df['SideADeaths'].fillna(0)
df['SideBDeaths'] = df['SideBDeaths'].fillna(0)
df['Deaths'] = (df['SideADeaths'] + df['SideBDeaths']).astype(int)

grouped = df.groupby('Initiator', as_index=False).agg({
    'WarID': 'first',
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
})

grouped = grouped.astype({
    'WarID': 'Int64',
    'PolityID': 'Int64',
    'PolityName': 'Int64',
    'StartMonth': 'Int64',
    'StartDay': 'Int64',
    'StartYear': 'Int64',
    'EndMonth': 'Int64',
    'EndDay': 'Int64',
    'EndYear': 'Int64',
    'Outcome': 'Int64',
    'Deaths': 'Int64'
})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_48/target_multisource_mcts.csv", index=False)