import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_89/training_0.csv", index_col=0)

joined = pd.merge(df, df, on="date", suffixes=('', '_y'))

agg = joined.groupby("date").agg({
    'ticker': 'first',
    'open': 'first',
    'high': 'first',
    'low': 'first',
    'close': 'first',
    'volume': 'first',
    'adj_close': 'first',
    'adj_volume': 'first',
    'ticker_y': 'first',
    'open_y': 'first',
    'high_y': 'first',
    'low_y': 'first',
    'close_y': 'first',
    'volume_y': 'first',
    'adj_close_y': 'first',
    'adj_volume_y': 'first'
}).reset_index()

agg['date'] = agg['date'].astype(str)

target_columns = ['date'] + [col for col in agg.columns if col != 'date']

result = agg[target_columns]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_89/target_multisource_mcts.csv", index=False)