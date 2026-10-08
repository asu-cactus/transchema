import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_87/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_87/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_87/training_2.csv", index_col=0)

pivot_df2 = df2.pivot(index='Rank', columns='Country', values='Rank').reset_index()

merged = pd.merge(pivot_df2, df0, left_on=pivot_df2.columns[1:], right_on='Country Name', how='inner')

# The target schema is ['Rank', '0'] with integer types.
# From the target examples, 'Rank' is integer, '0' is integer.
# The pivoted columns are country names, but target has only one column '0' besides Rank.
# The target examples show Rank and a single integer column named '0'.
# The pivoted df2 has Rank and many country columns with Rank values or NaN.
# The join merges on country names, but the target only has two columns.
# We need to extract the column named '0' from the pivoted df2 or from the merged data.

# The pivoted df2 columns after reset_index are: ['Rank', <country names>...]
# The target column '0' likely corresponds to the Rank value for a specific country or indicator.
# But the target examples show Rank and '0' column with integer values.
# The only way to get a single '0' column is to select the column named '0' from the pivoted df2.
# But no country is named '0', so maybe the '0' column is the first country column after pivot.
# The target examples show Rank and '0' column with values like 73, 85, 103.
# These values match the Rank values in df2 for some countries.

# So we take the first country column after 'Rank' in pivot_df2 as '0' column.
country_cols = list(pivot_df2.columns)
country_cols.remove('Rank')
first_country_col = country_cols[0]

result = pivot_df2[['Rank', first_country_col]].copy()
result.columns = ['Rank', '0']
result['Rank'] = result['Rank'].astype(int)
result['0'] = pd.to_numeric(result['0'], errors='coerce').fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_87/target_multisource_mcts.csv", index=False)