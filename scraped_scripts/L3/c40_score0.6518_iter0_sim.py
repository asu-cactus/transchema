import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_40/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_40/training_1.csv", index_col=0)

df_joined = pd.merge(df1, df0, on="Mouse ID")

df_grouped = df_joined.groupby(['Timepoint', 'Drug'])['Tumor Volume (mm3)'].mean().reset_index()

df_pivot = df_grouped.pivot(index='Timepoint', columns='Drug', values='Tumor Volume (mm3)').reset_index()

df_pivot.columns.name = None

target_cols = ['Timepoint', 'Capomulin', 'Ceftamin', 'Infubinol', 'Ketapril', 'Naftisol', 'Placebo', 'Propriva', 'Ramicane', 'Stelasyn', 'Zoniferol']

for col in target_cols:
    if col not in df_pivot.columns:
        df_pivot[col] = pd.NA

df_result = df_pivot[target_cols]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length3_40/target_multisource_mcts.csv", index=False)