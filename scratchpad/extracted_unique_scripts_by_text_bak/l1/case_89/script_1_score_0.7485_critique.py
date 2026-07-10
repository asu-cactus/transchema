import pandas as pd

# Read source table
source_path = "autopipeline-benchmarks/github-pipelines/length1_89/training_0.csv"
df = pd.read_csv(source_path, index_col=0)

# The source schema: ['ticker', 'date', 'open', 'high', 'low', 'close', 'volume', 'adj_close', 'adj_volume']
# The target schema has 'date' as first column, then columns named as floats (tickers), and last column 'price'.

# Convert ticker to string to match target column names
df['ticker'] = df['ticker'].astype(str)

# Pivot the table: index=date, columns=ticker, values=close (or price)
# The target last column is 'price', so we assume 'close' or 'price' is the value.
# Source has no 'price' column, but has 'close' which is likely the price.
pivot_df = df.pivot(index='date', columns='ticker', values='close')

# Reset index to have 'date' as a column
pivot_df.reset_index(inplace=True)

# The target schema columns are: 'date' + many float strings + 'price'
# The last column 'price' in target is likely the same as the last ticker column or a separate column.
# Since source has no separate 'price' column, we keep the pivoted columns as is.

# Sort columns to match target schema order: 'date' first, then sorted tickers as floats
# Convert column names (except 'date') to float for sorting
tickers = pivot_df.columns.drop('date')
tickers_float = sorted([float(t) for t in tickers])
tickers_str_sorted = [str(t) for t in tickers_float]

# Reorder columns
pivot_df = pivot_df[['date'] + tickers_str_sorted]

# Write to target CSV
pivot_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_89/target_multisource_mcts.csv", index=False)