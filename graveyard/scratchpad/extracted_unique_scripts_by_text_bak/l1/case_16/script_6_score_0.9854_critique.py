import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_16/training_0.csv", index_col=0)
df0_filtered = df0[df0['CUSTOMERNAME'].notnull() & df0['ORDERNUMBER'].notnull()]
df0_filtered['CUSTOMERNAME'] = df0_filtered['CUSTOMERNAME'].astype(str)
df0_filtered['ORDERNUMBER'] = df0_filtered['ORDERNUMBER'].astype(int)

# Group by CUSTOMERNAME and count ORDERNUMBER occurrences
df_grouped = df0_filtered.groupby('CUSTOMERNAME', as_index=False).agg({'ORDERNUMBER': 'count'})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_16/target_multisource_mcts.csv", index=False)