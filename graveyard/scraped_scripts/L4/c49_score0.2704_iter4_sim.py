import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_49/training_0.csv", index_col=0)

df_a = df[['WarNum', 'WarName', 'CcodeA', 'SideA', 'StartMonth1', 'StartDay1', 'StartYear1', 'EndMonth1', 'EndDay1', 'EndYear1', 'Initiator', 'Outcome', 'SideADeaths']]
df_b = df[['WarNum', 'WarName', 'CcodeB', 'SideB', 'StartMonth2', 'StartDay2', 'StartYear2', 'EndMonth2', 'EndDay2', 'EndYear2', 'Initiator', 'Outcome', 'SideBDeaths']]

df_a = df_a.rename(columns={
    'WarNum': 'WarID',
    'CcodeA': 'PolityID',
    'SideA': 'PolityName',
    'StartMonth1': 'StartMonth',
    'StartDay1': 'StartDay',
    'StartYear1': 'StartYear',
    'EndMonth1': 'EndMonth',
    'EndDay1': 'EndDay',
    'EndYear1': 'EndYear',
    'SideADeaths': 'Deaths'
})

df_b = df_b.rename(columns={
    'WarNum': 'WarID',
    'CcodeB': 'PolityID',
    'SideB': 'PolityName',
    'StartMonth2': 'StartMonth',
    'StartDay2': 'StartDay',
    'StartYear2': 'StartYear',
    'EndMonth2': 'EndMonth',
    'EndDay2': 'EndDay',
    'EndYear2': 'EndYear',
    'SideBDeaths': 'Deaths'
})

df_all = pd.concat([df_a, df_b], ignore_index=True)

df_all['PolityName'] = df_all['PolityName'].astype(str)
df_all['WarID'] = pd.to_numeric(df_all['WarID'], errors='coerce').astype('Int64')
df_all['PolityID'] = pd.to_numeric(df_all['PolityID'], errors='coerce').astype('Int64')
df_all['StartMonth'] = pd.to_numeric(df_all['StartMonth'], errors='coerce').fillna(0).astype(int)
df_all['StartDay'] = pd.to_numeric(df_all['StartDay'], errors='coerce').fillna(0).astype(int)
df_all['StartYear'] = pd.to_numeric(df_all['StartYear'], errors='coerce').fillna(0).astype(int)
df_all['EndMonth'] = pd.to_numeric(df_all['EndMonth'], errors='coerce').fillna(0).astype(int)
df_all['EndDay'] = pd.to_numeric(df_all['EndDay'], errors='coerce').fillna(0).astype(int)
df_all['EndYear'] = pd.to_numeric(df_all['EndYear'], errors='coerce').fillna(0).astype(int)

# Initiator and Outcome are categorical but target expects integer, map strings to integers if needed
# From source examples, Initiator and Outcome are integers or strings, so convert to string then map or convert to int if possible
def to_int_or_nan(x):
    try:
        return int(x)
    except:
        return pd.NA

df_all['Initiator'] = df_all['Initiator'].apply(to_int_or_nan).astype('Int64')
df_all['Outcome'] = df_all['Outcome'].apply(to_int_or_nan).astype('Int64')

df_all['Deaths'] = pd.to_numeric(df_all['Deaths'], errors='coerce').fillna(0).astype(int)

df_all = df_all[['PolityName', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_49/target_multisource_mcts.csv", index=False)