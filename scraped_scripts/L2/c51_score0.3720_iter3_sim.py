import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_51/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_51/training_1.csv", index_col=0)

df0['Tumor Volume (mm3)'] = pd.to_numeric(df0['Tumor Volume (mm3)'], errors='coerce')
df0['Metastatic Sites'] = pd.to_numeric(df0['Metastatic Sites'], errors='coerce')

grouped = df0.groupby(['Mouse ID', 'Timepoint'], as_index=False).agg({
    'Tumor Volume (mm3)': 'mean',
    'Metastatic Sites': 'sum'
})

merged = pd.merge(grouped, df1, on='Mouse ID', how='inner')

result = merged[['Drug', 'Timepoint', 'Mouse ID']]

result['Timepoint'] = pd.to_numeric(result['Timepoint'], errors='coerce').astype('Int64')
result['Mouse ID'] = result['Mouse ID'].astype(str)
result['Drug'] = result['Drug'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_51/target_multisource_mcts.csv", index=False)