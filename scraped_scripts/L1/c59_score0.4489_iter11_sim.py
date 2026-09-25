import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_59/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, on="ORDERNUMBER", suffixes=('_left', '_right'))

result = df_joined[['PRODUCTLINE_left', 'SALES_left']].copy()
result.columns = ['PRODUCTLINE', 'SALES']
result = result.dropna(subset=['PRODUCTLINE', 'SALES'])
result['PRODUCTLINE'] = result['PRODUCTLINE'].astype(str)
result['SALES'] = result['SALES'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_59/target_multisource_mcts.csv", index=False)