import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_50/training_0.csv", index_col=0)

df_a = df0[['WarNum', 'Outcome', 'CcodeA', 'SideA', 'StartMonth1', 'StartDay1', 'StartYear1', 'EndMonth1', 'EndDay1', 'EndYear1', 'Initiator', 'SideADeaths']].copy()
df_a.columns = ['WarID', 'Outcome', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Deaths']

df_b = df0[['WarNum', 'Outcome', 'CcodeB', 'SideB', 'StartMonth2', 'StartDay2', 'StartYear2', 'EndMonth2', 'EndDay2', 'EndYear2', 'Initiator', 'SideBDeaths']].copy()
df_b.columns = ['WarID', 'Outcome', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Deaths']

df = pd.concat([df_a, df_b], ignore_index=True)

# Convert columns to appropriate types
for col in ['Outcome', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Deaths']:
    df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

# Group by the leftmost columns (unique identifiers) and sum Deaths
group_cols = ['Outcome', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator']
df_grouped = df.groupby(group_cols, dropna=False, as_index=False).agg({'Deaths': 'sum'})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_50/target_multisource_mcts.csv", index=False)