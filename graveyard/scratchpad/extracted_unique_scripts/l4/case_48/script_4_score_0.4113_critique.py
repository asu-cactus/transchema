import pandas as pd

src0_path = "autopipeline-benchmarks/github-pipelines/length4_48/training_0.csv"

df0 = pd.read_csv(src0_path, index_col=0)

def to_int_or_zero(x):
    if pd.isna(x):
        return 0
    if isinstance(x, str):
        x = x.replace(',', '')
    try:
        return int(float(x))
    except:
        return 0

# Prepare side A data
df_sideA = pd.DataFrame()
df_sideA['Initiator'] = df0['Initiator']
df_sideA['WarID'] = df0['WarNum'].apply(to_int_or_zero)
df_sideA['PolityID'] = df0['CcodeA'].apply(to_int_or_zero)
df_sideA['PolityName'] = df0['CcodeB'].apply(to_int_or_zero)
df_sideA['StartMonth'] = df0['StartMonth1'].apply(to_int_or_zero)
df_sideA['StartDay'] = df0['StartDay1'].apply(to_int_or_zero)
df_sideA['StartYear'] = df0['StartYear1'].apply(to_int_or_zero)
df_sideA['EndMonth'] = df0['EndMonth1'].apply(to_int_or_zero)
df_sideA['EndDay'] = df0['EndDay1'].apply(to_int_or_zero)
df_sideA['EndYear'] = df0['EndYear1'].apply(to_int_or_zero)
df_sideA['Outcome'] = df0['Outcome'].apply(to_int_or_zero)
df_sideA['Deaths'] = df0['SideADeaths'].apply(to_int_or_zero)

# Prepare side B data
df_sideB = pd.DataFrame()
df_sideB['Initiator'] = df0['Initiator']
df_sideB['WarID'] = df0['WarNum'].apply(to_int_or_zero)
df_sideB['PolityID'] = df0['CcodeB'].apply(to_int_or_zero)
df_sideB['PolityName'] = df0['CcodeA'].apply(to_int_or_zero)
df_sideB['StartMonth'] = df0['StartMonth1'].apply(to_int_or_zero)
df_sideB['StartDay'] = df0['StartDay1'].apply(to_int_or_zero)
df_sideB['StartYear'] = df0['StartYear1'].apply(to_int_or_zero)
df_sideB['EndMonth'] = df0['EndMonth1'].apply(to_int_or_zero)
df_sideB['EndDay'] = df0['EndDay1'].apply(to_int_or_zero)
df_sideB['EndYear'] = df0['EndYear1'].apply(to_int_or_zero)
df_sideB['Outcome'] = df0['Outcome'].apply(to_int_or_zero)
df_sideB['Deaths'] = df0['SideBDeaths'].apply(to_int_or_zero)

# Concatenate side A and side B
df_all = pd.concat([df_sideA, df_sideB], ignore_index=True)

# Group by all columns except Deaths, sum Deaths
group_cols = ['Initiator', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear',
              'EndMonth', 'EndDay', 'EndYear', 'Outcome']

target_df = df_all.groupby(group_cols, dropna=False, as_index=False).agg({'Deaths': 'sum'})

# Write output
target_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_48/target_multisource_mcts.csv", index=False)