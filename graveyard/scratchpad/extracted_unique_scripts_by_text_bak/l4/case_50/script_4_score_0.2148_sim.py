import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_50/training_0.csv", index_col=0)

df = df0.copy()

df['Outcome'] = pd.to_numeric(df['Outcome'], errors='coerce').astype('Int64')

df['WarID'] = pd.to_numeric(df['WarNum'], errors='coerce').astype('Int64')
df['PolityID'] = pd.to_numeric(df['CcodeA'], errors='coerce').astype('Int64')
df['PolityName'] = pd.to_numeric(df['CcodeB'], errors='coerce').astype('Int64')

df['StartMonth'] = pd.to_numeric(df['StartMonth1'], errors='coerce').astype('Int64')
df['StartDay'] = pd.to_numeric(df['StartDay1'], errors='coerce').astype('Int64')
df['StartYear'] = pd.to_numeric(df['StartYear1'], errors='coerce').astype('Int64')

df['EndMonth'] = pd.to_numeric(df['EndMonth1'], errors='coerce').astype('Int64')
df['EndDay'] = pd.to_numeric(df['EndDay1'], errors='coerce').astype('Int64')
df['EndYear'] = pd.to_numeric(df['EndYear1'], errors='coerce').astype('Int64')

df['Initiator'] = pd.to_numeric(df['Initiator'], errors='coerce').astype('Int64')

side_a_deaths = pd.to_numeric(df['SideADeaths'], errors='coerce').fillna(0)
side_b_deaths = pd.to_numeric(df['SideBDeaths'], errors='coerce').fillna(0)
df['Deaths'] = (side_a_deaths + side_b_deaths).astype('Int64')

result = df[['Outcome', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear',
             'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Deaths']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_50/target_multisource_mcts.csv", index=False)