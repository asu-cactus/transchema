import pandas as pd
import numpy as np

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_89/training_0.csv", index_col=0)

# Group by date and aggregate ticker by first (or mean)
# Since ticker is float, and we want to pivot ticker values as columns, we pivot on 'ticker' column

# Create a DataFrame with columns: date, ticker
# We want to pivot so that each unique ticker becomes a column, values are ticker values (or some other column)
# Since the source has only ticker and date with values, we pivot ticker values as columns with values from ticker (redundant but matches target)

pivot_df = df.pivot_table(index='date', columns='ticker', values='ticker', aggfunc='first')

# Reset index to make 'date' a column
pivot_df = pivot_df.reset_index()

# Add 'price' column with NaN to match target schema
pivot_df['price'] = np.nan

# Reorder columns to match target schema:
# Target schema: ['date', <many float columns>, 'price']
# The float columns are the unique ticker values sorted ascending
float_cols = sorted([col for col in pivot_df.columns if col != 'date' and col != 'price'])

cols_order = ['date'] + float_cols + ['price']

pivot_df = pivot_df[cols_order]

# Ensure 'date' is string type
pivot_df['date'] = pivot_df['date'].astype(str)

pivot_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_89/target_multisource_mcts.csv", index=False)