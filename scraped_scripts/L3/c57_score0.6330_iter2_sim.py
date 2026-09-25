import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_57/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_57/training_1.csv", index_col=0)

df = pd.merge(df0, df1, on="Mouse ID")

grouped = df.groupby(["Timepoint", "Drug"], as_index=False)["Tumor Volume (mm3)"].mean()

pivoted = grouped.pivot(index="Timepoint", columns="Drug", values="Tumor Volume (mm3)")

pivoted = pivoted.reindex(columns=['Capomulin', 'Ceftamin', 'Infubinol', 'Ketapril', 'Naftisol', 'Placebo', 'Propriva', 'Ramicane', 'Stelasyn', 'Zoniferol'])

pivoted = pivoted.reset_index()

int_cols = ['Timepoint', 'Capomulin', 'Infubinol', 'Placebo', 'Propriva', 'Zoniferol']
for col in int_cols:
    if col in pivoted.columns:
        pivoted[col] = pivoted[col].round().astype('Int64')

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length3_57/target_multisource_mcts.csv", index=False)