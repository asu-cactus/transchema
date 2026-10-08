import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_51/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_51/training_1.csv", index_col=0)

df0['Mouse ID'] = df0['Mouse ID'].astype(str)
df1['Mouse ID'] = df1['Mouse ID'].astype(str)

grouped = df0.groupby(['Mouse ID', 'Timepoint'], as_index=False).agg(
    Tumor_Volume_Count=('Tumor Volume (mm3)', 'count'),
    Tumor_Volume_Sum=('Tumor Volume (mm3)', 'sum')
)

merged = pd.merge(grouped, df1, on='Mouse ID', how='inner')

merged['Timepoint'] = merged['Timepoint'].astype(int)
merged['Mouse ID'] = merged['Mouse ID'].apply(lambda x: int(''.join(filter(str.isdigit, x))) if any(c.isdigit() for c in x) else pd.NA)

result = merged[['Drug', 'Timepoint', 'Mouse ID']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_51/target_multisource_mcts.csv", index=False)