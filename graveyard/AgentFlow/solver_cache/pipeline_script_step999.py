import pandas as pd

# File paths for source CSVs
file_0 = "autopipeline-benchmarks/github-pipelines/length4_31/test_0.csv"  # Source4_31_0: ['County', 'm1403']
file_1 = "autopipeline-benchmarks/github-pipelines/length4_31/test_1.csv"  # Source4_31_1: ['County']
file_2 = "autopipeline-benchmarks/github-pipelines/length4_31/test_2.csv"  # Source4_31_2: ['County', 'm1401']
file_3 = "autopipeline-benchmarks/github-pipelines/length4_31/test_3.csv"  # Source4_31_3: ['County', 'm1402']
file_4 = "autopipeline-benchmarks/github-pipelines/length4_31/test_4.csv"  # Source4_31_4: ['County', 'm1404']

# Read source CSV files with index_col=0 as instructed
df_0 = pd.read_csv(file_0, index_col=0, dtype=str)
df_1 = pd.read_csv(file_1, index_col=0, dtype=str)
df_2 = pd.read_csv(file_2, index_col=0, dtype=str)
df_3 = pd.read_csv(file_3, index_col=0, dtype=str)
df_4 = pd.read_csv(file_4, index_col=0, dtype=str)

# Step 1: LEFT JOIN Source4_31_1 (County) with Source4_31_0 (County, m1403) on 'County'
step1 = pd.merge(df_1, df_0, on='County', how='left')

# Step 2: LEFT JOIN the result from Step 1 with Source4_31_2 (County, m1401) on 'County'
step2 = pd.merge(step1, df_2, on='County', how='left')

# Step 3: LEFT JOIN the result from Step 2 with Source4_31_3 (County, m1402) on 'County'
step3 = pd.merge(step2, df_3, on='County', how='left')

# Step 4: LEFT JOIN the result from Step 3 with Source4_31_4 (County, m1404) on 'County'
step4 = pd.merge(step3, df_4, on='County', how='left')

# Step 5: Handle 'NR' values by replacing them with None (NaN in pandas)
# Also ensure columns are strings as per target schema
def replace_nr_with_none(series):
    return series.where(series != 'NR', None)

final_df = step4.copy()
final_df['m1401'] = replace_nr_with_none(final_df['m1401'])
final_df['m1402'] = replace_nr_with_none(final_df['m1402'])
final_df['m1403'] = replace_nr_with_none(final_df['m1403'])
final_df['m1404'] = replace_nr_with_none(final_df['m1404'])

# Ensure the final dataframe has exactly the target schema columns in order
target_columns = ['County', 'm1401', 'm1402', 'm1403', 'm1404']
final_df = final_df[target_columns]

# Save the final dataframe to CSV
final_df.to_csv("Target4_31.csv", index=False)