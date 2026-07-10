import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_4.csv", index_col=0)

result_0 = pd.merge(df2, df0, how='inner', left_on='Ship_id', right_on='Ship_id')
result_1 = pd.merge(result_0, df4, how='inner', left_on='Ord_id', right_on='Ord_id')
result_2 = pd.merge(result_1, df1, how='inner', left_on='Prod_id', right_on='Prod_id')
result_3 = pd.merge(result_2, df3, how='inner', left_on='Cust_id', right_on='Cust_id')

target = result_3.groupby('Profit', as_index=False).size().rename(columns={'size':'Profit'})
# The above groupby with size() produces counts, but target schema expects Profit as float values, not counts.
# The partial plan says GROUP_BY : [Profit], but Profit is float and target schema is ['Profit': float].
# The target examples show Profit values, so likely the target is just the Profit column aggregated by sum or mean.
# Since Profit is float and target examples show float values, grouping by Profit itself is unusual.
# Instead, we should just select the Profit column from the joined data.
# The partial plan is ambiguous, but since target schema is only Profit, we can just select Profit column.

# So we just select the Profit column from the joined data:
target = result_3[['Profit']]

target.to_csv("autopipeline-benchmarks/github-pipelines/length5_87/target_multisource_mcts.csv", index=False)