import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length3_58/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length3_58/training_1.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length3_58/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

grouped = df0.groupby(['Mouse ID', 'Timepoint'], as_index=False)['Tumor Volume (mm3)'].mean()

merged = pd.merge(grouped, df1, on='Mouse ID', how='inner')

pivoted = merged.pivot_table(index='Timepoint', columns='Drug', values='Tumor Volume (mm3)', aggfunc='mean')

pivoted.columns.name = None
pivoted.reset_index(inplace=True)

target_cols = ['Timepoint', 'Capomulin', 'Ceftamin', 'Infubinol', 'Ketapril', 'Naftisol', 'Placebo', 'Propriva', 'Ramicane', 'Stelasyn', 'Zoniferol']
for col in target_cols:
    if col not in pivoted.columns:
        pivoted[col] = pd.NA

pivoted = pivoted[target_cols]

pivoted.to_csv(output_path, index=False)