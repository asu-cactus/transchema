import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_49/training_0.csv", index_col=0)

df = df0.copy()

# Create columns as per target schema without assignment
df['PolityName'] = df['WarName'].astype(str)
df['WarID'] = df['WarNum'].astype('Int64')
df['PolityID'] = 0

def coalesce_int(cols):
    for col in cols:
        if col in df.columns and df[col].notna().any():
            return df[col].astype('Int64')
    return pd.Series([pd.NA]*len(df), index=df.index, dtype='Int64')

df['StartMonth'] = coalesce_int(['StartMonth1', 'StartMonth2'])
df['StartDay'] = coalesce_int(['StartDay1', 'StartDay2'])
df['StartYear'] = coalesce_int(['StartYear1', 'StartYear2'])
df['EndMonth'] = coalesce_int(['EndMonth1', 'EndMonth2'])
df['EndDay'] = coalesce_int(['EndDay1', 'EndDay2'])
df['EndYear'] = coalesce_int(['EndYear1', 'EndYear2'])

# Initiator: convert to integer if possible, else 0
df['Initiator'] = pd.to_numeric(df['Initiator'], errors='coerce').astype('Int64').fillna(0)
df['Outcome'] = pd.to_numeric(df['Outcome'], errors='coerce').astype('Int64').fillna(0)

sideA_deaths = pd.to_numeric(df.get('SideADeaths', pd.Series(dtype='float')), errors='coerce').fillna(0).astype('Int64')
sideB_deaths = pd.to_numeric(df.get('SideBDeaths', pd.Series(dtype='float')), errors='coerce').fillna(0).astype('Int64')
df['Deaths'] = sideA_deaths + sideB_deaths

# Select columns for grouping and aggregation
group_cols = ['PolityName', 'WarID', 'PolityID']

agg_dict = {
    'StartMonth': 'min',
    'StartDay': 'min',
    'StartYear': 'min',
    'EndMonth': 'max',
    'EndDay': 'max',
    'EndYear': 'max',
    'Initiator': 'min',
    'Outcome': 'min',
    'Deaths': 'sum'
}

result = df.groupby(group_cols, dropna=False, as_index=False).agg(agg_dict)

# Ensure correct dtypes as per target schema
result['PolityName'] = result['PolityName'].astype(str)
result['WarID'] = result['WarID'].astype('Int64')
result['PolityID'] = result['PolityID'].astype('Int64')
result['StartMonth'] = result['StartMonth'].astype('Int64')
result['StartDay'] = result['StartDay'].astype('Int64')
result['StartYear'] = result['StartYear'].astype('Int64')
result['EndMonth'] = result['EndMonth'].astype('Int64')
result['EndDay'] = result['EndDay'].astype('Int64')
result['EndYear'] = result['EndYear'].astype('Int64')
result['Initiator'] = result['Initiator'].astype('Int64')
result['Outcome'] = result['Outcome'].astype('Int64')
result['Deaths'] = result['Deaths'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_49/target_multisource_mcts.csv", index=False)