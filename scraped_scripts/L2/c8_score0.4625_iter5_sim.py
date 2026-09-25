import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_8/training_1.csv", index_col=0)

agg = df0.groupby('Mouse ID').agg(
    Timepoint_count=('Timepoint', 'count'),
    Tumor_Volume_avg=('Tumor Volume (mm3)', 'mean'),
    Metastatic_Sites_max=('Metastatic Sites', 'max')
).reset_index()

merged = pd.merge(agg, df1, on='Mouse ID')

result = merged[['Drug', 'Timepoint_count', 'Mouse ID']].rename(columns={'Timepoint_count': 'Timepoint'})

result['Timepoint'] = result['Timepoint'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_8/target_multisource_mcts.csv", index=False)