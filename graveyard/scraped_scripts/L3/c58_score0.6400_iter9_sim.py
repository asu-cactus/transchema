import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_58/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_58/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="Mouse ID")

grouped = merged.groupby(["Timepoint", "Drug"], as_index=False)["Tumor Volume (mm3)"].sum()

pivoted = grouped.pivot(index="Timepoint", columns="Drug", values="Tumor Volume (mm3)")

pivoted = pivoted.reindex(columns=['Capomulin', 'Ceftamin', 'Infubinol', 'Ketapril', 'Naftisol', 'Placebo', 'Propriva', 'Ramicane', 'Stelasyn', 'Zoniferol'])

pivoted.index = pivoted.index.astype(int)
pivoted.columns.name = None
pivoted.reset_index(inplace=True)

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length3_58/target_multisource_mcts.csv", index=False)