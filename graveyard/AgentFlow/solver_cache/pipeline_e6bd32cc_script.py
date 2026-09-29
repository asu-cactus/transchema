import pandas as pd

# Define the source CSV paths
SOURCE_CSV_PATHS = {
    "Source4_31_0": "autopipeline-benchmarks/github-pipelines/length4_31/test_0.csv",
    "Source4_31_1": "autopipeline-benchmarks/github-pipelines/length4_31/test_1.csv",
    "Source4_31_2": "autopipeline-benchmarks/github-pipelines/length4_31/test_2.csv",
    "Source4_31_3": "autopipeline-benchmarks/github-pipelines/length4_31/test_3.csv",
    "Source4_31_4": "autopipeline-benchmarks/github-pipelines/length4_31/test_4.csv"
}

# Define the output CSV path
OUTPUT_CSV_PATH = "Target4_31.csv"

# Step 1: Read Source4_31_1 and Source4_31_0
df1 = pd.read_csv(SOURCE_CSV_PATHS["Source4_31_1"])
df0 = pd.read_csv(SOURCE_CSV_PATHS["Source4_31_0"], index_col=0)
temp1 = pd.merge(df1, df0, on='County', how='left')

# Step 2: Read Source4_31_2 and merge with temp1
df2 = pd.read_csv(SOURCE_CSV_PATHS["Source4_31_2"], index_col=0)
temp2 = pd.merge(temp1, df2, on='County', how='left')

# Step 3: Read Source4_31_3 and merge with temp2
df3 = pd.read_csv(SOURCE_CSV_PATHS["Source4_31_3"], index_col=0)
temp3 = pd.merge(temp2, df3, on='County', how='left')

# Step 4: Read Source4_31_4 and merge with temp3
df4 = pd.read_csv(SOURCE_CSV_PATHS["Source4_31_4"], index_col=0)
final_temp = pd.merge(temp3, df4, on='County', how='left')

# Step 5: Select the final columns to match the target schema
execution = final_temp[['County', 'm1401', 'm1402', 'm1403', 'm1404']]

# Save the final dataframe to the output CSV path
execution.to_csv(OUTPUT_CSV_PATH, index=False)