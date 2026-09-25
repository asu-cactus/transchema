import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_59/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_59/training_0.csv", index_col=0)

df_union = pd.concat([df0, df1], ignore_index=True)

result = df_union.groupby('PRODUCTLINE', as_index=False)['SALES'].sum()

result['PRODUCTLINE'] = result['PRODUCTLINE'].astype(str)
result['SALES'] = result['SALES'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_59/target_multisource_mcts.csv", index=False)