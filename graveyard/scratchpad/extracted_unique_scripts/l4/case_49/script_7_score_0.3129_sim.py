import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_49/training_0.csv", index_col=0)

df = df0.copy()

df['PolityName'] = df['SideA'].fillna('') + df['SideB'].fillna('')
df['PolityName'] = df['PolityName'].replace('', pd.NA)

df['WarID'] = pd.to_numeric(df['WarNum'], errors='coerce').astype('Int64')

df['PolityID'] = pd.to_numeric(df['CcodeA'], errors='coerce').astype('Int64')

df['StartMonth'] = pd.to_numeric(df['StartMonth1'], errors='coerce').astype('Int64')
df['StartDay'] = pd.to_numeric(df['StartDay1'], errors='coerce').astype('Int64')
df['StartYear'] = pd.to_numeric(df['StartYear1'], errors='coerce').astype('Int64')

df['EndMonth'] = pd.to_numeric(df['EndMonth1'], errors='coerce').astype('Int64')
df['EndDay'] = pd.to_numeric(df['EndDay1'], errors='coerce').astype('Int64')
df['EndYear'] = pd.to_numeric(df['EndYear1'], errors='coerce').astype('Int64')

df['Initiator'] = pd.to_numeric(df['Initiator'], errors='coerce').astype('Int64')
df['Outcome'] = pd.to_numeric(df['Outcome'], errors='coerce').astype('Int64')

sideA_deaths = pd.to_numeric(df['SideADeaths'], errors='coerce').fillna(0)
sideB_deaths = pd.to_numeric(df['SideBDeaths'], errors='coerce').fillna(0)
df['Deaths'] = (sideA_deaths + sideB_deaths).astype('Int64')

result = df[['PolityName', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_49/target_multisource_mcts.csv", index=False)