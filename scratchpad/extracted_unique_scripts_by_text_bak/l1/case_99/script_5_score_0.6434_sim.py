import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_99/training_0.csv", index_col=0)

agg = df0.groupby(
    ['user_id', 'timestamp', 'source', 'device', 'operative_system', 'test'],
    as_index=False
).agg({'price': 'sum', 'converted': 'sum'})

agg['user_id'] = agg['user_id'].astype(int)
agg['test'] = agg['test'].astype(int)
agg['price'] = agg['price'].astype(int)
agg['converted'] = agg['converted'].astype(int)
agg['timestamp'] = agg['timestamp'].astype(str)
agg['source'] = agg['source'].astype(str)
agg['device'] = agg['device'].astype(str)
agg['operative_system'] = agg['operative_system'].astype(str)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_99/target_multisource_mcts.csv", index=False)