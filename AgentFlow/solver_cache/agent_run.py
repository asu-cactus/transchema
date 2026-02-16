import pandas as pd

# Define source CSV paths
SOURCE_CSV_PATHS = {
    "Source4_31_1": "path/to/Source4_31_1.csv",
    "Source4_31_2": "path/to/Source4_31_2.csv",
    "Source4_31_3": "path/to/Source4_31_3.csv",
    "Source4_31_0": "path/to/Source4_31_0.csv",
    "Source4_31_4": "path/to/Source4_31_4.csv"
}

# Define output CSV path
OUTPUT_CSV_PATH = "path/to/Target4_31.csv"

# Step 1: Read Source4_31_1 from CSV without index_col=0 into df_1
df_1 = pd.read_csv(SOURCE_CSV_PATHS["Source4_31_1"])

# Step 2: Read Source4_31_2 from CSV without index_col=0 into df_2
df_2 = pd.read_csv(SOURCE_CSV_PATHS["Source4_31_2"])

# Step 3: Read Source4_31_3 from CSV without index_col=0 into df_3
df_3 = pd.read_csv(SOURCE_CSV_PATHS["Source4_31_3"])

# Step 4: Read Source4_31_0 from CSV without index_col=0 into df_0
df_0 = pd.read_csv(SOURCE_CSV_PATHS["Source4_31_0"])

# Step 5: Read Source4_31_4 from CSV without index_col=0 into df_4
df_4 = pd.read_csv(SOURCE_CSV_PATHS["Source4_31_4"])

# Step 6: Left join df_1 with df_2 on 'County' to add 'm1401'
result_1 = df_1.merge(df_2[['County', 'm1401']], on='County', how='left')

# Step 7: Left join result_1 with df_3 on 'County' to add 'm1402'
result_2 = result_1.merge(df_3[['County', 'm1402']], on='County', how='left')

# Step 8: Left join result_2 with df_0 on 'County' to add 'm1403'
result_3 = result_2.merge(df_0[['County', 'm1403']], on='County', how='left')

# Step 9: Left join result_3 with df_4 on 'County' to add 'm1404'
result_4 = result_3.merge(df_4[['County', 'm1404']], on='County', how='left')

# Step 10: Replace missing or 'NR' values in measurement columns with pd.NA
measurement_columns = ['m1401', 'm1402', 'm1403', 'm1404']
for col in measurement_columns:
    result_4[col] = result_4[col].replace(['NR', ''], pd.NA)

# Step 11: Select columns ['County', 'm1401', 'm1402', 'm1403', 'm1404'] as final output schema for Target4_31
execution = result_4[['County', 'm1401', 'm1402', 'm1403', 'm1404']]

# Save execution to OUTPUT_CSV_PATH
execution.to_csv(OUTPUT_CSV_PATH, index=False)