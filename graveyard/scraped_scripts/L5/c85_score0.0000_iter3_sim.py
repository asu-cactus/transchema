import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_1.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_4.csv", index_col=0)

s0['Order_ID'] = s0['Order_ID'].astype(str)
s1['Order_ID'] = s1['Order_ID'].astype(str)
union_result = pd.concat([s0, s1], ignore_index=True)

s4['Ord_id'] = s4['Ord_id'].astype(str)
merged = pd.merge(union_result, s4, left_on='Order_ID', right_on='Ord_id', how='inner')

result = merged.groupby('Sales', as_index=False).size()
result = merged.groupby('Sales', as_index=False).agg({'Sales':'sum'})
result = merged[['Sales']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_85/target_multisource_mcts.csv", index=False)