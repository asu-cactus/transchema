import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_70/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_70/training_1.csv", index_col=0)

merged = pd.merge(df0[['order_id', 'order_status', 'order_approved_at']], 
                  df1[['order_id', 'product_id', 'seller_id', 'price', 'freight_value']], 
                  on='order_id')

merged = merged.astype({
    'order_id': 'string',
    'order_status': 'string',
    'order_approved_at': 'string',
    'product_id': 'string',
    'seller_id': 'string',
    'price': 'float',
    'freight_value': 'float'
})

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_70/target_multisource_mcts.csv", index=False)