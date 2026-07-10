import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_79/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_79/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_79/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_79/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_79/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Convert columns to numeric with Int64 dtype to allow NaNs
df['PolityName'] = pd.to_numeric(df['PolityName'], errors='coerce').astype('Int64')
df['StartYear'] = pd.to_numeric(df['StartYear'], errors='coerce').astype('Int64')
df['StartMonth'] = pd.to_numeric(df['StartMonth'], errors='coerce').astype('Int64')
df['StartDay'] = pd.to_numeric(df['StartDay'], errors='coerce').astype('Int64')
df['EndYear'] = pd.to_numeric(df['EndYear'], errors='coerce').astype('Int64')
df['EndMonth'] = pd.to_numeric(df['EndMonth'], errors='coerce').astype('Int64')
df['EndDay'] = pd.to_numeric(df['EndDay'], errors='coerce').astype('Int64')
df['Outcome'] = pd.to_numeric(df['Outcome'], errors='coerce').astype('Int64')
df['Deaths'] = pd.to_numeric(df['Deaths'], errors='coerce').astype('Int64')

# Group by Initiator and WarID, sum other columns
agg_dict = {
    'PolityName': 'sum',
    'StartYear': 'sum',
    'StartMonth': 'sum',
    'StartDay': 'sum',
    'EndYear': 'sum',
    'EndMonth': 'sum',
    'EndDay': 'sum',
    'Outcome': 'sum',
    'Deaths': 'sum'
}

df_grouped = df.groupby(['Initiator', 'WarID'], dropna=False, as_index=False).agg(agg_dict)

# Reorder columns to match target schema
df_grouped = df_grouped[['Initiator', 'WarID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay',
                         'EndYear', 'EndMonth', 'EndDay', 'Outcome', 'Deaths']]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_79/target_multisource_mcts.csv", index=False)