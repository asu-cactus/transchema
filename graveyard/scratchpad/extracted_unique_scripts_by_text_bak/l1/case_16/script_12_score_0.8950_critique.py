import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_16/training_0.csv", index_col=0)

df0 = df0.dropna(subset=['ORDERNUMBER', 'CUSTOMERNAME'])
df0 = df0[df0['ORDERNUMBER'].apply(lambda x: str(x).isdigit())]

result = df0.groupby('CUSTOMERNAME', as_index=False).agg({'ORDERNUMBER': pd.Series.nunique})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_16/target_multisource_mcts.csv", index=False)