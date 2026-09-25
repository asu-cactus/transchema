import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_85/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_85/training_1.csv", index_col=0)

df0['Mouse ID'] = df0['Mouse ID'].astype(str)
df1['Mouse ID'] = df1['Mouse ID'].astype(str)

pivot_df1 = df1.copy()
pivot_df1 = pivot_df1.drop_duplicates(subset=['Mouse ID'])
pivot_df1 = pivot_df1.rename(columns={'Drug': 'Drug'})

pivot_df0 = df0.copy()
pivot_df0['Timepoint'] = pd.to_numeric(pivot_df0['Timepoint'], errors='coerce')

merged = pd.merge(pivot_df1, pivot_df0, on=['Mouse ID'], how='inner')

result = merged[['Drug', 'Timepoint', 'Mouse ID']].copy()
result['Timepoint'] = result['Timepoint'].astype('Int64')
result['Mouse ID'] = result['Mouse ID'].astype(int, errors='ignore')

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_85/target_multisource_mcts.csv", index=False)