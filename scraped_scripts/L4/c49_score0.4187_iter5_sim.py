import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_49/training_0.csv", index_col=0)

df = df0.copy()

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
try:
    df['Initiator'] = pd.to_numeric(df['Initiator'], errors='coerce').astype('Int64')
except:
    df['Initiator'] = 0

df['Outcome'] = pd.to_numeric(df['Outcome'], errors='coerce').astype('Int64')

sideA_deaths = pd.to_numeric(df.get('SideADeaths', pd.Series(dtype='float')), errors='coerce').fillna(0).astype('Int64')
sideB_deaths = pd.to_numeric(df.get('SideBDeaths', pd.Series(dtype='float')), errors='coerce').fillna(0).astype('Int64')
df['Deaths'] = sideA_deaths + sideB_deaths

result = df[['PolityName', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear',
             'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_49/target_multisource_mcts.csv", index=False)