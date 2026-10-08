import pandas as pd

# Read source table
source_path = "autopipeline-benchmarks/github-pipelines/length1_89/training_0.csv"
df = pd.read_csv(source_path, index_col=0)

# The source columns: ['ticker', 'date', 'open', 'high', 'low', 'close', 'volume', 'adj_close', 'adj_volume']
# We pivot on 'date' and 'ticker', values from 'close' (price)

# Drop rows with missing 'date', 'ticker', or 'close' to avoid NaNs in pivot
df_clean = df.dropna(subset=['date', 'ticker', 'close'])

# Pivot: index=date, columns=ticker, values=close
pivot_df = df_clean.pivot(index='date', columns='ticker', values='close')

# Sort columns by ticker ascending (float)
pivot_df = pivot_df.reindex(sorted(pivot_df.columns), axis=1)

# Reset index to have 'date' as a column
pivot_df = pivot_df.reset_index()

# Add 'price' column as mean of all ticker columns per date (ignoring NaNs)
pivot_df['price'] = pivot_df.loc[:, pivot_df.columns != 'date'].mean(axis=1)

# Ensure columns order: 'date' first, then tickers as floats (string column names), then 'price'
cols = ['date'] + [col for col in pivot_df.columns if col not in ['date', 'price']] + ['price']
pivot_df = pivot_df[cols]

# Write output
pivot_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_89/target_multisource_mcts.csv", index=False)