import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_89/training_0.csv", index_col=0)
df = source0.copy()
df['date'] = df['date'].astype(str)
grouped = df.groupby('date', as_index=False).agg({
    'ticker': 'first',
    'open': 'first',
    'high': 'first',
    'low': 'first',
    'close': 'first',
    'volume': 'first',
    'adj_close': 'first',
    'adj_volume': 'first'
})

# The target schema has 'date' plus many float columns named as floats and a 'price' column.
# The source has no columns matching those float-named columns.
# The only columns that can be used to produce those float-named columns are 'ticker' (which looks like float strings),
# and 'close' or 'price' (close or adj_close).
# The target columns look like many float numbers as column names, plus a 'price' column.
# The source has 'ticker' which looks like float numbers as strings, and 'close' or 'adj_close' as float values.
# So we need to pivot the data: rows with date, ticker, close -> columns with ticker as column names, values as close.
# Then add a 'price' column if needed (likely from close or adj_close).

# Prepare for pivot: keep date, ticker, close
pivot_df = df[['date', 'ticker', 'close']].copy()
pivot_df['ticker'] = pivot_df['ticker'].astype(str)
pivot_df['close'] = pd.to_numeric(pivot_df['close'], errors='coerce')

pivoted = pivot_df.pivot_table(index='date', columns='ticker', values='close', aggfunc='first')

# The target columns are sorted float strings plus 'price' at the end.
# The pivoted columns are tickers as strings, which correspond to float strings.
# We convert columns to float and sort them ascending.
pivoted.columns = pivoted.columns.astype(float)
pivoted = pivoted.reindex(sorted(pivoted.columns), axis=1)

# Add 'price' column as the mean of all close prices per date (or NaN if no data)
pivoted['price'] = pivoted.mean(axis=1)

# Reset index to have 'date' as a column
result = pivoted.reset_index()

# Convert 'date' to string to match target schema
result['date'] = result['date'].astype(str)

# Reorder columns: 'date' first, then sorted float columns, then 'price'
cols = ['date'] + sorted([col for col in result.columns if col not in ['date', 'price']]) + ['price']
result = result[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_89/target_multisource_mcts.csv", index=False)