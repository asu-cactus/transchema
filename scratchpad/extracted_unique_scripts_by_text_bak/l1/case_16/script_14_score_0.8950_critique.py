import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_16/training_0.csv", index_col=0)
df0 = df0[['CUSTOMERNAME', 'ORDERNUMBER']].dropna(subset=['CUSTOMERNAME', 'ORDERNUMBER'])
df0['ORDERNUMBER'] = pd.to_numeric(df0['ORDERNUMBER'], errors='coerce')
df0 = df0.dropna(subset=['ORDERNUMBER'])
df0['ORDERNUMBER'] = df0['ORDERNUMBER'].astype(int)
result = df0.groupby('CUSTOMERNAME', as_index=False).agg({'ORDERNUMBER': pd.Series.nunique})
result = result.rename(columns={'ORDERNUMBER': 'ORDERNUMBER'})
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_16/target_multisource_mcts.csv", index=False)