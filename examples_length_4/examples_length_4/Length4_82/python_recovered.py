import pandas as pd

# File paths for the sources
source0_path = 'autopipeline-benchmarks/github-pipelines/length4_82/test_0.csv'  # ['Institution', 'year 2016']
source1_path = 'autopipeline-benchmarks/github-pipelines/length4_82/test_1.csv'  # ['Institution', 'year 2014']
source2_path = 'autopipeline-benchmarks/github-pipelines/length4_82/test_2.csv'  # ['Institution', '(Fall 2000)', ... , '(Fall 2014)']
source3_path = 'autopipeline-benchmarks/github-pipelines/length4_82/test_3.csv'  # ['Institution', 'year 2015']
source4_path = 'autopipeline-benchmarks/github-pipelines/length4_82/test_4.csv'  # ['Institution', 'Cohort 2014', 'Cohort 2015', 'Cohort 2016']

# Load all sources with index_col=0 to ignore CSV numeric index column
df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)
df2 = pd.read_csv(source2_path, index_col=0)
df3 = pd.read_csv(source3_path, index_col=0)
df4 = pd.read_csv(source4_path, index_col=0)

# Step 1: Normalize Institution names by stripping whitespaces for better joins
for df in [df0, df1, df2, df3, df4]:
    df['Institution'] = df['Institution'].str.strip()

# Step 2: Rename year columns in df0, df1, df3 to match target schema naming convention
df0_renamed = df0.rename(columns={'year 2016': 'persist 2016'})
df1_renamed = df1.rename(columns={'year 2014': 'persist 2014'})
df3_renamed = df3.rename(columns={'year 2015': 'persist 2015'})

# Step 3: Select only relevant columns from df2 corresponding to target columns for Fall years
fall_cols = ['Institution', '(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)']
df2_selected = df2[fall_cols].copy()

# Step 4: Join all persistence year data (persist 2014, persist 2015, persist 2016) by Institution
df_persist = df1_renamed[['Institution', 'persist 2014']].merge(
    df3_renamed[['Institution', 'persist 2015']],
    on='Institution',
    how='outer'
).merge(
    df0_renamed[['Institution', 'persist 2016']],
    on='Institution',
    how='outer'
)

# Step 5: Merge fall semester data (df2_selected) with persistence data (df_persist) on Institution
df_merge = df2_selected.merge(df_persist, on='Institution', how='outer')

# Step 6: Merge cohort data (df4) ['Institution', 'Cohort 2014', 'Cohort 2015', 'Cohort 2016']
df_final = df_merge.merge(df4, on='Institution', how='outer')

# Step 7: Ensure all target columns exist; if missing, fill with NaNs or appropriate dtype
target_columns = [
    'Institution',
    '(Fall 2011)',
    '(Fall 2012)',
    '(Fall 2013)',
    '(Fall 2014)',
    'persist 2014',
    'persist 2015',
    'persist 2016',
    'Cohort 2014',
    'Cohort 2015',
    'Cohort 2016'
]

for col in target_columns:
    if col not in df_final.columns:
        # Add missing columns with suitable dtype: floats for fall years, integers for persist/cohort
        if col.startswith('(Fall'):
            df_final[col] = pd.NA
        elif col.startswith('persist') or col.startswith('Cohort'):
            df_final[col] = pd.NA

# Step 8: Reorder columns to target schema order
df_final = df_final[target_columns]

# Step 9: Convert data types to match target schema:
# - 'Institution': string
df_final['Institution'] = df_final['Institution'].astype(str)

# - '(Fall xxxx)': float
for col in ['(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)']:
    df_final[col] = pd.to_numeric(df_final[col], errors='coerce')

# - 'persist xxxx': integer (but allow for NaNs, use Int64 nullable integer dtype)
for col in ['persist 2014', 'persist 2015', 'persist 2016']:
    df_final[col] = pd.to_numeric(df_final[col], errors='coerce').astype('Int64')

# - 'Cohort xxxx': integer (nullable)
for col in ['Cohort 2014', 'Cohort 2015', 'Cohort 2016']:
    df_final[col] = pd.to_numeric(df_final[col], errors='coerce').astype('Int64')

# Step 10: Drop rows where 'Institution' is missing or empty string after trimming
df_final = df_final[df_final['Institution'].str.strip() != '']
df_final = df_final.dropna(subset=['Institution'])

# Step 11: Sort by Institution (optional for nicer output)
df_final = df_final.sort_values(by='Institution').reset_index(drop=True)

# Step 12: Write the resulting dataframe to the specified target path
target_path = 'autopipeline-benchmarks/github-pipelines/length4_82/target_multisource_cot.csv'
df_final.to_csv(target_path, index=False)