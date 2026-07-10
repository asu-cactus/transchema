import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_57/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_57/training_1.csv", index_col=0)

df_joined = pd.merge(df1, df0, on="Mouse ID")

pivot = df_joined.pivot_table(index="Timepoint", columns="Drug", values="Tumor Volume (mm3)", aggfunc="max")

pivot = pivot.reset_index()

expected_cols = ['Timepoint', 'Capomulin', 'Ceftamin', 'Infubinol', 'Ketapril', 'Naftisol', 'Placebo', 'Propriva', 'Ramicane', 'Stelasyn', 'Zoniferol']

for col in expected_cols:
    if col not in pivot.columns:
        pivot[col] = pd.NA

pivot = pivot[expected_cols]

pivot['Timepoint'] = pivot['Timepoint'].astype(int)
for col in expected_cols[1:]:
    # According to target schema: some columns int, some float
    # Capomulin: int, Ceftamin: float, Infubinol: int, Ketapril: float, Naftisol: float, Placebo: int, Propriva: int, Ramicane: float, Stelasyn: float, Zoniferol: int
    if col in ['Ceftamin', 'Ketapril', 'Naftisol', 'Ramicane', 'Stelasyn']:
        pivot[col] = pd.to_numeric(pivot[col], errors='coerce').astype(float)
    else:
        pivot[col] = pd.to_numeric(pivot[col], errors='coerce').astype('Int64')

pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_57/target_multisource_mcts.csv", index=False)