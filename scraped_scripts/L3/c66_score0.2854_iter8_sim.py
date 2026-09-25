import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length3_66/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length3_66/training_1.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length3_66/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

pivot0 = df0.pivot_table(index='Timepoint', columns='Mouse ID', values='Tumor Volume (mm3)', aggfunc='first')

pivot1 = df1.pivot(index='Mouse ID', columns='Drug', values='Drug')

merged = pivot0.T.join(pivot1, how='left').T

merged.columns.name = None
merged.index.name = 'Timepoint'

merged = merged.reset_index()

drug_names = ['Capomulin', 'Ceftamin', 'Infubinol', 'Ketapril', 'Naftisol', 'Placebo', 'Propriva', 'Ramicane', 'Stelasyn', 'Zoniferol']

for drug in drug_names:
    if drug not in merged.columns:
        merged[drug] = pd.NA

merged = merged[['Timepoint'] + drug_names]

for col in ['Timepoint', 'Capomulin', 'Infubinol', 'Placebo', 'Propriva', 'Zoniferol']:
    merged[col] = pd.to_numeric(merged[col], errors='coerce').astype('Int64')

for col in ['Ceftamin', 'Ketapril', 'Naftisol', 'Ramicane', 'Stelasyn']:
    merged[col] = pd.to_numeric(merged[col], errors='coerce').astype(float)

merged.to_csv(output_path, index=False)