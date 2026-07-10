import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length3_60/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length3_60/training_1.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length3_60/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

grouped = df0.groupby(['Timepoint', 'Mouse ID'], as_index=False)['Tumor Volume (mm3)'].mean()

merged = pd.merge(grouped, df1, on='Mouse ID', how='inner')

pivot = merged.pivot_table(index='Timepoint', columns='Drug', values='Tumor Volume (mm3)', aggfunc='mean')

pivot = pivot.reindex(columns=['Capomulin', 'Ceftamin', 'Infubinol', 'Ketapril', 'Naftisol', 'Placebo', 'Propriva', 'Ramicane', 'Stelasyn', 'Zoniferol'])

pivot.reset_index(inplace=True)

pivot.to_csv(output_path, index=False)