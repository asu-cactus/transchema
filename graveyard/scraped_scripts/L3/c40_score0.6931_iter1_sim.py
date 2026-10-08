import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_40/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_40/training_1.csv", index_col=0)

df = pd.merge(df1, df0, on="Mouse ID")

df_pivot = df.pivot_table(index="Timepoint", columns="Drug", values="Tumor Volume (mm3)", aggfunc='first')

df_pivot = df_pivot.reindex(columns=['Capomulin', 'Ceftamin', 'Infubinol', 'Ketapril', 'Naftisol', 'Placebo', 'Propriva', 'Ramicane', 'Stelasyn', 'Zoniferol'])

df_pivot.reset_index(inplace=True)

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_40/target_multisource_mcts.csv", index=False)