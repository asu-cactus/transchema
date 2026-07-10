import pandas as pd

# Read source table
source_path = "autopipeline-benchmarks/github-pipelines/length1_89/training_0.csv"
df = pd.read_csv(source_path, index_col=0)

# The source has columns: ticker (float), date (string), open, high, low, close, volume, adj_close, adj_volume
# We want to pivot on date (rows) and ticker (columns), aggregating adj_close by mean

# Ensure ticker is string to match target column names (which are strings of floats)
df['ticker'] = df['ticker'].astype(str)

# Group by date and ticker, aggregate adj_close by mean
grouped = df.groupby(['date', 'ticker'], as_index=False)['adj_close'].mean()

# Pivot so that tickers become columns, date is index
pivoted = grouped.pivot(index='date', columns='ticker', values='adj_close')

# Reset index to make date a column
pivoted.reset_index(inplace=True)

# The target schema has a last column named 'price' which is not in source
# Add 'price' column with NaN values to match target schema
pivoted['price'] = pd.NA

# Reorder columns to match target schema:
# Target schema columns: ['date', <ticker columns as strings>, 'price']
# The ticker columns in target are floats as strings, so sort columns accordingly

# Extract ticker columns from target schema (excluding 'date' and 'price')
# Since we don't have the exact list here, we use the columns from pivoted except 'date' and 'price'
ticker_cols = [col for col in pivoted.columns if col not in ['date', 'price']]

# Sort ticker columns as floats ascending to match target schema order
ticker_cols_sorted = sorted(ticker_cols, key=lambda x: float(x))

# Final column order
final_cols = ['date'] + ticker_cols_sorted + ['price']

# Reindex columns accordingly (some tickers may be missing, so fill missing columns with NaN)
pivoted = pivoted.reindex(columns=final_cols)

# Write output
pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length1_89/target_multisource_mcts.csv", index=False)