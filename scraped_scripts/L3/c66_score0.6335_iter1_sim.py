import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_66/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_66/training_1.csv", index_col=0)

df = pd.merge(df0, df1, on="Mouse ID")

df_pivot = df.pivot_table(index="Timepoint", columns="Drug", values="Tumor Volume (mm3)", aggfunc="mean")

df_pivot = df_pivot.reset_index()

df_pivot.columns.name = None

df_pivot = df_pivot.rename(columns={
    'Capomulin': 'Capomulin',
    'Ceftamin': 'Ceftamin',
    'Infubinol': 'Infubinol',
    'Ketapril': 'Ketapril',
    'Naftisol': 'Naftisol',
    'Placebo': 'Placebo',
    'Propriva': 'Propriva',
    'Ramicane': 'Ramicane',
    'Stelasyn': 'Stelasyn',
    'Zoniferol': 'Zoniferol'
})

df_pivot['Timepoint'] = df_pivot['Timepoint'].astype(int)

for col in ['Capomulin', 'Infubinol', 'Placebo', 'Propriva', 'Zoniferol']:
    if col in df_pivot.columns:
        df_pivot[col] = df_pivot[col].round().astype('Int64')

for col in ['Ceftamin', 'Ketapril', 'Naftisol', 'Ramicane', 'Stelasyn']:
    if col in df_pivot.columns:
        df_pivot[col] = df_pivot[col].astype(float)

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_66/target_multisource_mcts.csv", index=False)