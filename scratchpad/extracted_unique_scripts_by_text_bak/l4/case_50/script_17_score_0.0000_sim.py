import pandas as pd

sideA_path = "autopipeline-benchmarks/github-pipelines/length4_50/training_0_sideA.csv"
sideB_path = "autopipeline-benchmarks/github-pipelines/length4_50/training_0_sideB.csv"

df_sideA = pd.read_csv(sideA_path, index_col=0)
df_sideB = pd.read_csv(sideB_path, index_col=0)

df = pd.concat([df_sideA, df_sideB], ignore_index=True)

df = df.rename(columns={
    'Outcome': 'Outcome',
    'WarNum': 'WarID',
    'CcodeA': 'PolityID',
    'SideA': 'PolityName',
    'StartMonth1': 'StartMonth',
    'StartDay1': 'StartDay',
    'StartYear1': 'StartYear',
    'EndMonth1': 'EndMonth',
    'EndDay1': 'EndDay',
    'EndYear1': 'EndYear',
    'Initiator': 'Initiator',
    'SideADeaths': 'Deaths'
})

df = df[['Outcome', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Deaths']]

df['Outcome'] = pd.to_numeric(df['Outcome'], errors='coerce').astype('Int64')
df['WarID'] = pd.to_numeric(df['WarID'], errors='coerce').astype('Int64')
df['PolityID'] = pd.to_numeric(df['PolityID'], errors='coerce').astype('Int64')
df['PolityName'] = pd.to_numeric(df['PolityName'], errors='coerce').astype('Int64')
df['StartMonth'] = pd.to_numeric(df['StartMonth'], errors='coerce').astype('Int64')
df['StartDay'] = pd.to_numeric(df['StartDay'], errors='coerce').astype('Int64')
df['StartYear'] = pd.to_numeric(df['StartYear'], errors='coerce').astype('Int64')
df['EndMonth'] = pd.to_numeric(df['EndMonth'], errors='coerce').astype('Int64')
df['EndDay'] = pd.to_numeric(df['EndDay'], errors='coerce').astype('Int64')
df['EndYear'] = pd.to_numeric(df['EndYear'], errors='coerce').astype('Int64')
df['Initiator'] = pd.to_numeric(df['Initiator'], errors='coerce').astype('Int64')
df['Deaths'] = pd.to_numeric(df['Deaths'], errors='coerce').astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_50/target_multisource_mcts.csv", index=False)