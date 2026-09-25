import pandas as pd

# Define source file paths
source_files = [
    'autopipeline-benchmarks/github-pipelines/length4_94/test_0.csv',
    'autopipeline-benchmarks/github-pipelines/length4_94/test_1.csv',
    'autopipeline-benchmarks/github-pipelines/length4_94/test_2.csv',
    'autopipeline-benchmarks/github-pipelines/length4_94/test_3.csv'
]

# Read all source files into a list of dataframes
dfs = [pd.read_csv(f, index_col=0) for f in source_files]

# Concatenate (union) all dataframes
df_all = pd.concat(dfs, ignore_index=True)

# Ensure column order is exactly as target schema
target_columns = ['Split', 'SubjectId', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']
df_all = df_all[target_columns]

# Enforce data types based on target schema
df_all['Split'] = df_all['Split'].astype(str)
df_all['SubjectId'] = df_all['SubjectId'].astype(int)
# Subject column appears integer in target examples, but source contains strings (e.g., "HitterId", "PitcherId"),
# thus needs numeric conversion. Since target examples have integer values for Subject=SubjectId,
# we convert Subject column values to int by replacing string values by SubjectId (per target examples).
# So replace all values in 'Subject' column to equal the 'SubjectId' column values.
df_all['Subject'] = df_all['SubjectId'].astype(int)

# Convert remaining columns to int
int_cols = ['PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']
df_all[int_cols] = df_all[int_cols].astype(int)

# Save the resulting dataframe to the target CSV file path
output_path = 'autopipeline-benchmarks/github-pipelines/length4_94/target_multisource_cot.csv'
df_all.to_csv(output_path, index=False)