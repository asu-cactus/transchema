import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_16/training_0.csv", index_col=0)

df0 = df0.dropna(subset=['ORDERNUMBER', 'CUSTOMERNAME'])
df0 = df0[df0['ORDERNUMBER'].apply(lambda x: str(x).isdigit())]
df0['ORDERNUMBER'] = df0['ORDERNUMBER'].astype(int)

joined = pd.merge(df0, df0, on='ORDERNUMBER', suffixes=('_left', '_right'))

result = joined.groupby('CUSTOMERNAME_left', as_index=False).agg({'ORDERNUMBER': 'first'})

result = result.rename(columns={'CUSTOMERNAME_left': 'CUSTOMERNAME'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_16/target_multisource_mcts.csv", index=False)