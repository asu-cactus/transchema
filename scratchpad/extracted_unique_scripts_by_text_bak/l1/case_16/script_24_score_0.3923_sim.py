import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_16/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_16/training_0.csv", index_col=0)

joined = pd.merge(df0, df1, on="ORDERNUMBER", suffixes=('_left', '_right'))

unioned = pd.concat([df0, df1], ignore_index=True)

result = unioned[['CUSTOMERNAME', 'ORDERNUMBER']].copy()
result['ORDERNUMBER'] = pd.to_numeric(result['ORDERNUMBER'], errors='coerce').astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_16/target_multisource_mcts.csv", index=False)