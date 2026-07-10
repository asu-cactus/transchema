import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_4.csv", index_col=0)

df0 = df0.dropna(subset=['age_grp'])
df2 = df2.dropna(subset=['age_grp'])
df4 = df4.dropna(subset=['age_grp'])

df02 = pd.merge(df0, df2, on='age_grp', suffixes=('_0', '_2'))
df024 = pd.merge(df02, df4, on='age_grp', suffixes=('', '_4'))

agg = df024.groupby('age_grp').agg({
    'Count_0': 'sum',
    'Count_2': 'sum',
    'Count': 'sum',
    'Rate_0': 'mean',
    'Rate_2': 'mean',
    'Rate': 'mean'
}).reset_index()

agg['Count'] = agg['Count_0'] + agg['Count_2'] + agg['Count']
agg['Rate'] = (agg['Rate_0'] + agg['Rate_2'] + agg['Rate']) / 3

agg = agg[['age_grp', 'Count', 'Rate']]

agg['Notes'] = pd.NA
agg['Statistics'] = pd.NA

agg = agg[['age_grp', 'Count', 'Notes', 'Rate', 'Statistics']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_84/target_multisource_mcts.csv", index=False)