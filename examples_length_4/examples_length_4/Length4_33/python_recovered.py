import pandas as pd

# File paths for source CSVs
source0_path = 'autopipeline-benchmarks/github-pipelines/length4_33/test_0.csv'  # ['batsman', 'batsman_runs']
source1_path = 'autopipeline-benchmarks/github-pipelines/length4_33/test_1.csv'  # ['batsman', 'total_runs']
source2_path = 'autopipeline-benchmarks/github-pipelines/length4_33/test_2.csv'  # ['batsman', 'total_runs']
source3_path = 'autopipeline-benchmarks/github-pipelines/length4_33/test_3.csv'  # ['batsman', 'batsman_runs']
source4_path = 'autopipeline-benchmarks/github-pipelines/length4_33/test_4.csv'  # ['batsman', 'batsman_runs']

# Read sources with index_col=0 to ignore indexing column
df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)
df2 = pd.read_csv(source2_path, index_col=0)
df3 = pd.read_csv(source3_path, index_col=0)
df4 = pd.read_csv(source4_path, index_col=0)

# Rename columns to prepare for joining - suffix columns to distinguish sources
# Sources 0,3,4 have 'batsman_runs' - rename as batsman_runs_x, batsman_runs_y, batsman_runs respectively as per target
df0_ren = df0.rename(columns={'batsman_runs':'batsman_runs_x'})
df3_ren = df3.rename(columns={'batsman_runs':'batsman_runs_y'})
df4_ren = df4.rename(columns={'batsman_runs':'batsman_runs'})

# Sources 1,2 have 'total_runs' - rename for target as total_runs_x (source1), total_runs_y (source2)
df1_ren = df1.rename(columns={'total_runs':'total_runs_x'})
df2_ren = df2.rename(columns={'total_runs':'total_runs_y'})

# Similarly, from source0 and source3 we also want total_runs_x and total_runs_y columns: 
# But source0 and source3 do not have total_runs columns, so no rename.

# According to target schema, we expect these columns:
# ['batsman', 'batsman_runs_x', 'total_runs_x', 'total_runs_y', 'batsman_runs_y', 'batsman_runs']

# Perform outer joins on 'batsman' key stepwise to keep maximum data
# Join df0_ren and df1_ren
df01 = pd.merge(df0_ren, df1_ren, on='batsman', how='outer')

# Join the result with df2_ren
df012 = pd.merge(df01, df2_ren, on='batsman', how='outer')

# Join with df3_ren
df0123 = pd.merge(df012, df3_ren, on='batsman', how='outer')

# Join with df4_ren
df_final = pd.merge(df0123, df4_ren, on='batsman', how='outer')

# After joins, some columns might be missing/null per row; fill NaNs for numeric columns with 0 or appropriate
# According to target examples, batsman_runs_x is float, total_runs_x and total_runs_y int, batsman_runs_y int, batsman_runs int.

# Cast the data types accordingly and handle missing values:
df_final['batsman_runs_x'] = df_final['batsman_runs_x'].astype(float)

# The total_runs_x and total_runs_y columns came from source1 and source2 with integer values
# Because of outer join, NaNs can appear => fill with 0 then convert to int
df_final['total_runs_x'] = df_final['total_runs_x'].fillna(0).astype(int)
df_final['total_runs_y'] = df_final['total_runs_y'].fillna(0).astype(int)

# batsman_runs_y and batsman_runs come from df3 and df4, fill NaNs with 0 and convert to int
df_final['batsman_runs_y'] = df_final['batsman_runs_y'].fillna(0).astype(int)
df_final['batsman_runs'] = df_final['batsman_runs'].fillna(0).astype(int)

# The target has column 'batsman' as string, which is already string dtype by default, ensure it explicitly
df_final['batsman'] = df_final['batsman'].astype(str)

# Sort rows by batsman if desired (not mandatory, but for consistent output)
df_final = df_final.sort_values(by='batsman').reset_index(drop=True)

# Select columns exactly in target schema order:
df_target = df_final[['batsman', 'batsman_runs_x', 'total_runs_x', 'total_runs_y', 'batsman_runs_y', 'batsman_runs']]

# Save to CSV without the index column
output_path = "autopipeline-benchmarks/github-pipelines/length4_33/target_multisource_cot.csv"
df_target.to_csv(output_path, index=False)