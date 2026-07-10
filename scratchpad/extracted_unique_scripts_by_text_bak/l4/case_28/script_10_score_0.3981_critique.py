import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_3.csv", index_col=0)

# Concatenate all source tables (UNION)
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Normalize INCIDENT_TYPE to uppercase and strip spaces
df_all['INCIDENT_TYPE'] = df_all['INCIDENT_TYPE'].str.upper().str.strip()

# Convert ULCS_NO to int
df_all['ULCS_NO'] = df_all['ULCS_NO'].astype(int)

# Extract the first 4 digits of SCHOOL_YEAR and convert to int
df_all['SCHOOL_YEAR'] = df_all['SCHOOL_YEAR'].str.extract(r'(\d{4})').astype(int)

# Convert INCIDENT_COUNT and SCHOOL_ID to int
df_all['INCIDENT_COUNT'] = df_all['INCIDENT_COUNT'].astype(int)
df_all['SCHOOL_ID'] = df_all['SCHOOL_ID'].astype(int)

# Group by the leftmost columns and sum INCIDENT_COUNT
df_grouped = df_all.groupby(['INCIDENT_TYPE', 'ULCS_NO', 'SCHOOL_YEAR', 'SCHOOL_ID'], as_index=False)['INCIDENT_COUNT'].sum()

# Reorder columns to match target schema
df_grouped = df_grouped[['INCIDENT_TYPE', 'ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_COUNT', 'SCHOOL_ID']]

# Write to target CSV
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_28/target_multisource_mcts.csv", index=False)