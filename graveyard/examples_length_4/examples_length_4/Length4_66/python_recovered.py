import pandas as pd

# File paths of source CSV files
source_paths = [
    'autopipeline-benchmarks/github-pipelines/length4_66/test_0.csv',
    'autopipeline-benchmarks/github-pipelines/length4_66/test_1.csv',
    'autopipeline-benchmarks/github-pipelines/length4_66/test_2.csv',
    'autopipeline-benchmarks/github-pipelines/length4_66/test_3.csv',
    'autopipeline-benchmarks/github-pipelines/length4_66/test_4.csv'
]

# Read all source files into a list of dataframes
# Use index_col=0 to ignore the numerical index column as stated
dfs = [pd.read_csv(path, index_col=0) for path in source_paths]

# All source tables have exactly the same schema:
# ['Year', 'Category', 'Nominee', 'Movie', 'Winner']
# and the target schema is the same.
# According to the instructions and hints:
# - Union all source tables (concatenate rows)
# - No further transformation required as schemas match exactly,
#   and columns match target columns with expected types.
# - Make sure columns order and types are respected.

# Concatenate all source dataframes (union operation)
combined_df = pd.concat(dfs, ignore_index=True)

# According to the example and hints:
# - The 'Winner' column in source and target looks like strings such as 'YES', no transformation needed
# - The 'Year' column is string (e.g., "2010 (83rd)")
# - The other columns are strings as well

# Ensure column order matches target schema exactly:
target_columns = ['Year', 'Category', 'Nominee', 'Movie', 'Winner']
combined_df = combined_df[target_columns]

# Ensure all columns are string type (as in target schema)
for col in target_columns:
    combined_df[col] = combined_df[col].astype(str)

# Export the combined DataFrame to the target CSV path
combined_df.to_csv('autopipeline-benchmarks/github-pipelines/length4_66/target_multisource_cot.csv', index=False)