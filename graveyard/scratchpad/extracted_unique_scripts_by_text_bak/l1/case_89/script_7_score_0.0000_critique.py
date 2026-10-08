import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_89/training_0.csv", index_col=0)
df = source0.copy()

df['date'] = df['date'].astype(str)
df['ticker'] = df['ticker'].astype(str)
df['close'] = pd.to_numeric(df['close'], errors='coerce')

pivoted = df.pivot_table(index='date', columns='ticker', values='close', aggfunc='first')
pivoted.columns = pivoted.columns.astype(float)
pivoted = pivoted.reindex(sorted(pivoted.columns), axis=1)

pivoted['price'] = pivoted.mean(axis=1)

result = pivoted.reset_index()
result['date'] = result['date'].astype(str)

cols = ['date'] + sorted([col for col in result.columns if col not in ['date', 'price']]) + ['price']
result = result[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_89/target_multisource_mcts.csv", index=False)