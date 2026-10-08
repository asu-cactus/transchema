import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_50/training_0.csv", index_col=0)

# Combine CcodeA and CcodeB into PolityID, SideA and SideB into PolityName
df0['PolityID'] = df0['CcodeA'].combine_first(df0['CcodeB'])
df0['PolityName'] = df0['SideA'].combine_first(df0['SideB'])

def to_int_safe(x):
    if pd.isna(x):
        return pd.NA
    if isinstance(x, str):
        x = x.replace(',', '')
    try:
        return int(float(x))
    except:
        return pd.NA

cols_to_int = ['Outcome', 'WarNum', 'PolityID', 'StartMonth1', 'StartDay1', 'StartYear1',
               'EndMonth1', 'EndDay1', 'EndYear1', 'Initiator', 'SideADeaths', 'SideBDeaths']

for c in cols_to_int:
    if c in df0.columns:
        df0[c] = df0[c].apply(to_int_safe)

# Sum deaths from both sides
df0['Deaths'] = df0[['SideADeaths', 'SideBDeaths']].sum(axis=1, min_count=1)

# Rename columns to target schema names
df0.rename(columns={
    'Outcome': 'Outcome',
    'WarNum': 'WarID',
    'PolityID': 'PolityID',
    'PolityName': 'PolityName',
    'StartMonth1': 'StartMonth',
    'StartDay1': 'StartDay',
    'StartYear1': 'StartYear',
    'EndMonth1': 'EndMonth',
    'EndDay1': 'EndDay',
    'EndYear1': 'EndYear',
    'Initiator': 'Initiator',
}, inplace=True)

target_cols = ['Outcome', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear',
               'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Deaths']

df = df0[target_cols]

# Group by all columns except Deaths, sum Deaths
group_by_cols = ['Outcome', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear',
                 'EndMonth', 'EndDay', 'EndYear', 'Initiator']

result = df.groupby(group_by_cols, dropna=False, as_index=False).agg({'Deaths': 'sum'})

# Convert columns to int where possible (except PolityName which is string)
int_cols = ['Outcome', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear',
            'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Deaths']

for c in int_cols:
    if c in result.columns:
        result[c] = pd.to_numeric(result[c], errors='coerce').fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_50/target_multisource_mcts.csv", index=False)