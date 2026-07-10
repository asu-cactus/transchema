import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_99/training_0.csv", index_col=0)

agg = df0.groupby(['source', 'device', 'operative_system']).agg(
    user_id=('user_id', 'count'),
    price=('price', 'sum'),
    converted=('converted', 'sum')
).reset_index()

agg['user_id'] = agg['user_id'].astype(int)
agg['price'] = agg['price'].astype(int)
agg['converted'] = agg['converted'].astype(int)

agg['timestamp'] = ''
agg['test'] = 0

agg = agg[['user_id', 'timestamp', 'source', 'device', 'operative_system', 'test', 'price', 'converted']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_99/target_multisource_mcts.csv", index=False)