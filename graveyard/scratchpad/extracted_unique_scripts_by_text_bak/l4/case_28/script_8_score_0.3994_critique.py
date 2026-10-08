import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_3.csv", index_col=0)

# UNION all source tables
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Normalize INCIDENT_TYPE strings: strip and uppercase to reduce duplicates due to case differences
df_all['INCIDENT_TYPE'] = df_all['INCIDENT_TYPE'].astype(str).str.strip()

# Convert SCHOOL_YEAR from string like '2014-2015' to integer 2014 (start year)
# Extract the first 4 digits as integer
df_all['SCHOOL_YEAR'] = df_all['SCHOOL_YEAR'].astype(str).str[:4].astype(int)

# GROUP BY the key columns and sum INCIDENT_COUNT
df_grouped = df_all.groupby(
    ['INCIDENT_TYPE', 'ULCS_NO', 'SCHOOL_YEAR', 'SCHOOL_ID'], dropna=False, as_index=False
).agg({'INCIDENT_COUNT': 'sum'})

# Ensure correct types as per target schema
df_grouped['INCIDENT_TYPE'] = df_grouped['INCIDENT_TYPE'].astype(str)
df_grouped['ULCS_NO'] = df_grouped['ULCS_NO'].astype(int)
df_grouped['SCHOOL_YEAR'] = df_grouped['SCHOOL_YEAR'].astype(int)
df_grouped['SCHOOL_ID'] = df_grouped['SCHOOL_ID'].astype(int)
df_grouped['INCIDENT_COUNT'] = df_grouped['INCIDENT_COUNT'].astype(int)

# Reorder columns to match target schema exactly
df_grouped = df_grouped[['INCIDENT_TYPE', 'ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_COUNT', 'SCHOOL_ID']]

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_28/target_multisource_mcts.csv", index=False)