import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_48/training_0.csv", index_col=0)

# Cast WarNum to WarID integer
df0['WarID'] = df0['WarNum'].astype('Int64')

# PolityID and PolityName from CcodeA as integer
df0['PolityID'] = df0['CcodeA'].astype('Int64')
df0['PolityName'] = df0['CcodeA'].astype('Int64')

# Functions to choose start and end dates from first or second period
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

# Convert deaths columns to numeric, fill NaN with 0, then sum
df0['SideADeaths'] = pd.to_numeric(df0['SideADeaths'], errors='coerce').fillna(0).astype('Int64')
df0['SideBDeaths'] = pd.to_numeric(df0['SideBDeaths'], errors='coerce').fillna(0).astype('Int64')
df0['Deaths'] = df0['SideADeaths'] + df0['SideBDeaths']

# Group by the leftmost non-float unique columns in target schema
group_cols = ['Initiator', 'WarID', 'PolityID', 'PolityName']

agg_dict = {
    'StartMonth': 'min',
    'StartDay': 'min',
    'StartYear': 'min',
    'EndMonth': 'min',
    'EndDay': 'min',
    'EndYear': 'min',
    'Outcome': 'min',
    'Deaths': 'sum'
}

result = df0[group_cols + list(agg_dict.keys())].groupby(group_cols, dropna=False, as_index=False).agg(agg_dict)

# Ensure correct dtypes as per target schema
result['WarID'] = result['WarID'].astype('Int64')
result['PolityID'] = result['PolityID'].astype('Int64')
result['PolityName'] = result['PolityName'].astype('Int64')
result['StartMonth'] = result['StartMonth'].astype('Int64')
result['StartDay'] = result['StartDay'].astype('Int64')
result['StartYear'] = result['StartYear'].astype('Int64')
result['EndMonth'] = result['EndMonth'].astype('Int64')
result['EndDay'] = result['EndDay'].astype('Int64')
result['EndYear'] = result['EndYear'].astype('Int64')
result['Outcome'] = result['Outcome'].astype('Int64')
result['Deaths'] = result['Deaths'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_48/target_multisource_mcts.csv", index=False)