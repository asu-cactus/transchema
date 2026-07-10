import pandas as pd

source_path = "autopipeline-benchmarks/github-pipelines/length1_93/training_0.csv"
df = pd.read_csv(source_path, index_col=0)

joined = pd.merge(df, df, on=['user_id', 'time'], how='inner', suffixes=('', '_dup'))

grouped = joined.groupby('time', as_index=False).agg({
    'user_id': 'first',
    'bet': 'sum',
    'win': 'sum'
})

grouped['user_id'] = grouped['user_id'].astype(str)
grouped['time'] = grouped['time'].astype(str)
grouped['bet'] = grouped['bet'].astype(float)
grouped['win'] = grouped['win'].astype(float)

grouped = grouped[['user_id', 'time', 'bet', 'win']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_93/target_multisource_mcts.csv", index=False)