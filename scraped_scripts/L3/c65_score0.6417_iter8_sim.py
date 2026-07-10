import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_65/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_65/training_1.csv", index_col=0)

grouped = df1.groupby(['Timepoint', 'Mouse ID']).agg({'Metastatic Sites':'mean'}).reset_index()
merged = pd.merge(grouped, df0, on='Mouse ID', how='inner')

agg = merged.groupby(['Timepoint', 'Drug']).agg({'Metastatic Sites':'mean'}).reset_index()

pivot = agg.pivot(index='Timepoint', columns='Drug', values='Metastatic Sites')

pivot = pivot.reindex(columns=['Capomulin', 'Ceftamin', 'Infubinol', 'Ketapril', 'Naftisol', 'Placebo', 'Propriva', 'Ramicane', 'Stelasyn', 'Zoniferol'])

pivot.index = pivot.index.astype(int)
pivot.columns.name = None
pivot.reset_index(inplace=True)

pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_65/target_multisource_mcts.csv", index=False)