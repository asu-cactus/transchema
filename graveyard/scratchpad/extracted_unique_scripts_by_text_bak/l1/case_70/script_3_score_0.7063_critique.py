import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_70/training_0.csv")
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_70/training_1.csv")

merged = pd.merge(
    df0[['order_id', 'order_status', 'order_approved_at']],
    df1[['order_id', 'product_id', 'seller_id', 'price', 'freight_value']],
    on='order_id',
    how='inner'
)

merged['price'] = merged['price'].astype(float)
merged['freight_value'] = merged['freight_value'].astype(float)

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_70/target_multisource_mcts.csv", index=False)