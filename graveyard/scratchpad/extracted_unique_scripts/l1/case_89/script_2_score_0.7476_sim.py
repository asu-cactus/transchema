import pandas as pd

src_path = "autopipeline-benchmarks/github-pipelines/length1_89/training_0.csv"
df = pd.read_csv(src_path, index_col=0)

df['date'] = df['date'].astype(str)
df_unpivot = df.melt(id_vars=['ticker', 'date'], value_vars=['open', 'high', 'low', 'close', 'volume', 'adj_close', 'adj_volume'], var_name='price', value_name='value')

df_unpivot['ticker'] = df_unpivot['ticker'].astype(str)
df_unpivot['price'] = df_unpivot['price'].astype(str)

df_pivot = df_unpivot.pivot_table(index='date', columns='ticker', values='value', aggfunc='first')

df_pivot.columns = df_pivot.columns.astype(str)
df_pivot.reset_index(inplace=True)

target_cols = ['date'] + sorted([col for col in df_pivot.columns if col != 'date'], key=lambda x: float(x) if x.replace('.','',1).isdigit() else float('inf'))
df_pivot = df_pivot[target_cols]

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_89/target_multisource_mcts.csv", index=False)