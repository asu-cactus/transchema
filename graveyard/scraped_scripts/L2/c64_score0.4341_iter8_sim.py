import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_64/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_64/training_1.csv", index_col=0)

df1_grouped = df1.groupby(['Mouse ID', 'Timepoint']).agg(
    Metastatic_Sites_min=('Metastatic Sites', 'min'),
    Metastatic_Sites_max=('Metastatic Sites', 'max'),
    Metastatic_Sites_avg=('Metastatic Sites', 'mean')
).reset_index()

df1_grouped = df1_grouped.merge(df0, on='Mouse ID', how='left')

result = df1_grouped[['Drug', 'Timepoint', 'Mouse ID']]

result['Timepoint'] = result['Timepoint'].astype(int)
result['Mouse ID'] = result['Mouse ID'].astype(str)
result['Drug'] = result['Drug'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_64/target_multisource_mcts.csv", index=False)