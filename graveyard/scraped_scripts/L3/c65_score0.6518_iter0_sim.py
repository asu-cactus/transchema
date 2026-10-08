import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_65/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_65/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="Mouse ID")

grouped = merged.groupby(['Timepoint', 'Drug'])['Tumor Volume (mm3)'].mean().reset_index()

pivoted = grouped.pivot(index='Timepoint', columns='Drug', values='Tumor Volume (mm3)').reset_index()

pivoted.columns.name = None

pivoted = pivoted.rename(columns={
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

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length3_65/target_multisource_mcts.csv", index=False)