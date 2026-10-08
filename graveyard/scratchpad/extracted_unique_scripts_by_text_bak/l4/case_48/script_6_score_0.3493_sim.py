import pandas as pd

src0_path = "autopipeline-benchmarks/github-pipelines/length4_48/training_0.csv"

df0 = pd.read_csv(src0_path, index_col=0)

df_sideA = df0[['Initiator', 'Outcome', 'SideADeaths']].copy()
df_sideA.rename(columns={'SideADeaths': 'Deaths'}, inplace=True)
df_sideA['Side'] = 'A'

df_sideB = df0[['Initiator', 'Outcome', 'SideBDeaths']].copy()
df_sideB.rename(columns={'SideBDeaths': 'Deaths'}, inplace=True)
df_sideB['Side'] = 'B'

union_df = pd.concat([df_sideA, df_sideB], ignore_index=True)

joined = pd.merge(df0, union_df, how='inner', on=['Initiator', 'Outcome'])

def to_int_or_zero(x):
    if pd.isna(x):
        return 0
    if isinstance(x, str):
        x = x.replace(',', '')
    try:
        return int(float(x))
    except:
        return 0

joined['WarID'] = joined['WarNum'].apply(to_int_or_zero)
joined['PolityID'] = joined['CcodeA'].apply(to_int_or_zero)
joined['PolityName'] = joined['CcodeB'].apply(to_int_or_zero)

joined['StartMonth'] = joined['StartMonth1'].apply(to_int_or_zero)
joined['StartDay'] = joined['StartDay1'].apply(to_int_or_zero)
joined['StartYear'] = joined['StartYear1'].apply(to_int_or_zero)
joined['EndMonth'] = joined['EndMonth1'].apply(to_int_or_zero)
joined['EndDay'] = joined['EndDay1'].apply(to_int_or_zero)
joined['EndYear'] = joined['EndYear1'].apply(to_int_or_zero)

joined['Outcome'] = joined['Outcome'].apply(to_int_or_zero)

joined['Deaths'] = joined['Deaths'].apply(to_int_or_zero)

target_df = joined[['Initiator', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Outcome', 'Deaths']]

target_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_48/target_multisource_mcts.csv", index=False)