import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_50/training_0.csv", index_col=0)

df0['PolityID'] = df0['CcodeA'].combine_first(df0['CcodeB']).astype('Int64')
df0['PolityName'] = df0['SideA'].combine_first(df0['SideB'])
df0['StartMonth'] = df0['StartMonth1'].combine_first(df0['StartMonth2']).astype('Int64')
df0['StartDay'] = df0['StartDay1'].combine_first(df0['StartDay2']).astype('Int64')
df0['StartYear'] = df0['StartYear1'].combine_first(df0['StartYear2']).astype('Int64')
df0['EndMonth'] = df0['EndMonth1'].combine_first(df0['EndMonth2']).astype('Int64')
df0['EndDay'] = df0['EndDay1'].combine_first(df0['EndDay2']).astype('Int64')
df0['EndYear'] = df0['EndYear1'].combine_first(df0['EndYear2']).astype('Int64')

df0['Outcome'] = df0['Outcome'].astype('Int64')
df0['WarID'] = df0['WarNum'].astype('Int64')
df0['Initiator'] = pd.to_numeric(df0['Initiator'], errors='coerce').astype('Int64')

sideA_deaths = pd.to_numeric(df0['SideADeaths'], errors='coerce').fillna(0)
sideB_deaths = pd.to_numeric(df0['SideBDeaths'], errors='coerce').fillna(0)
df0['Deaths'] = (sideA_deaths + sideB_deaths).astype('Int64')

result = df0[['Outcome', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear',
              'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Deaths']]

group_cols = ['Outcome', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear',
              'EndMonth', 'EndDay', 'EndYear', 'Initiator']

result = result.groupby(group_cols, dropna=False, as_index=False).agg({'Deaths': 'sum'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_50/target_multisource_mcts.csv", index=False)