import pandas as pd

source_path = "autopipeline-benchmarks/github-pipelines/length1_93/training_0.csv"
df = pd.read_csv(source_path, index_col=0)

joined = pd.merge(df, df, on="user_id", suffixes=('_left', '_right'))

grouped = joined.groupby('time_left', as_index=False).agg({
    'user_id': 'first',
    'bet_left': 'sum',
    'win_left': 'sum'
})

result = grouped.rename(columns={
    'time_left': 'time',
    'bet_left': 'bet',
    'win_left': 'win'
})

result = result.astype({
    'user_id': 'string',
    'time': 'string',
    'bet': 'float',
    'win': 'float'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_93/target_multisource_mcts.csv", index=False)