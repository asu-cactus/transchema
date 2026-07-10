import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_57/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_57/training_1.csv", index_col=0)

agg_df1 = df1.groupby(['Mouse ID', 'Timepoint']).agg({'Metastatic Sites':'sum', 'Tumor Volume (mm3)':'min'}).reset_index()

merged = pd.merge(agg_df1, df0, on='Mouse ID', how='inner')

pivot = merged.pivot_table(index='Timepoint', columns='Drug', values='Metastatic Sites', aggfunc='sum')

pivot = pivot.reset_index()

pivot.columns.name = None

target_cols = ['Timepoint', 'Capomulin', 'Ceftamin', 'Infubinol', 'Ketapril', 'Naftisol', 'Placebo', 'Propriva', 'Ramicane', 'Stelasyn', 'Zoniferol']

for col in target_cols:
    if col not in pivot.columns:
        pivot[col] = pd.NA

pivot = pivot[target_cols]

pivot = pivot.astype({
    'Timepoint': 'int64',
    'Capomulin': 'Int64',
    'Ceftamin': 'float64',
    'Infubinol': 'Int64',
    'Ketapril': 'float64',
    'Naftisol': 'float64',
    'Placebo': 'Int64',
    'Propriva': 'Int64',
    'Ramicane': 'float64',
    'Stelasyn': 'float64',
    'Zoniferol': 'Int64'
})

pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_57/target_multisource_mcts.csv", index=False)