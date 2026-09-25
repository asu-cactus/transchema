import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_99/training_0.csv", index_col=0)

agg_df = df0.groupby(
    ['user_id', 'timestamp', 'source', 'device', 'operative_system'],
    as_index=False
).agg(
    test=('test', 'count'),
    price=('price', 'sum'),
    converted=('converted', 'sum')
)

agg_df['user_id'] = agg_df['user_id'].astype(int)
agg_df['timestamp'] = agg_df['timestamp'].astype(str)
agg_df['source'] = agg_df['source'].astype(str)
agg_df['device'] = agg_df['device'].astype(str)
agg_df['operative_system'] = agg_df['operative_system'].astype(str)
agg_df['test'] = agg_df['test'].astype(int)
agg_df['price'] = agg_df['price'].astype(int)
agg_df['converted'] = agg_df['converted'].astype(int)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_99/target_multisource_mcts.csv", index=False)