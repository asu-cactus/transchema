import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_67/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_67/training_1.csv", index_col=0)

grouped_df0 = df0.groupby('user_id', as_index=False).agg({
    'timestamp': 'first',
    'source': 'first',
    'device': 'first',
    'operative_system': 'first',
    'test': 'first',
    'price': 'first',
    'converted': 'first'
})

merged = pd.merge(grouped_df0, df1[['user_id', 'city']], on='user_id', how='left')

merged = merged[['user_id', 'timestamp', 'source', 'device', 'operative_system', 'test', 'price', 'converted', 'city']]

merged.to_csv("autopipeline-benchmarks/github-pipelines/length2_67/target_multisource_mcts.csv", index=False)