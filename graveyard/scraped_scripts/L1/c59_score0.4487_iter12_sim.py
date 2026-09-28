import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_59/training_0.csv", index_col=0)
df_joined = pd.merge(df, df, on="PRODUCTCODE", suffixes=('_left', '_right'))
df_result = df_joined[['PRODUCTLINE_left', 'SALES_left']].copy()
df_result.columns = ['PRODUCTLINE', 'SALES']
df_result = df_result.dropna(subset=['PRODUCTLINE', 'SALES'])
df_result['SALES'] = df_result['SALES'].astype(float)
df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_59/target_multisource_mcts.csv", index=False)