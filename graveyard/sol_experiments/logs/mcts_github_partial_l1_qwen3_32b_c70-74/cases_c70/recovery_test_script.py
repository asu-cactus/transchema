import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_70/test_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_70/test_1.csv', index_col=0)

merged_df = pd.merge(df1, df0, on='order_id')

result = merged_df[['order_id', 'order_status', 'order_approved_at', 'product_id', 'seller_id', 'price', 'freight_value']]

result.to_csv('autopipeline-benchmarks/github-pipelines/length1_70/target_multisource_mcts_recovery_test_val.csv')