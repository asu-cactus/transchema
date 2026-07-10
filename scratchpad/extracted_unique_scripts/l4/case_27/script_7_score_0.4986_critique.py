import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_3.csv", index_col=0)

# Align columns of df2 to match others
df2 = df2[['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

# Concatenate all source tables (UNION)
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Ensure correct types
df_all['ULCS_NO'] = df_all['ULCS_NO'].astype(int)
df_all['SCHOOL_ID'] = df_all['SCHOOL_ID'].astype(int)
df_all['INCIDENT_COUNT'] = df_all['INCIDENT_COUNT'].astype(int)
df_all['SCHOOL_YEAR'] = df_all['SCHOOL_YEAR'].astype(str)
df_all['INCIDENT_TYPE'] = df_all['INCIDENT_TYPE'].astype(str)

# Group by keys and aggregate sum of INCIDENT_COUNT
df_grouped = df_all.groupby(['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'SCHOOL_ID'], as_index=False).agg({'INCIDENT_COUNT': 'sum'})

# Convert INCIDENT_TYPE to integer codes to match target schema
df_grouped['INCIDENT_TYPE'] = pd.factorize(df_grouped['INCIDENT_TYPE'])[0]

# Reorder columns as per target schema
df_grouped = df_grouped[['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_27/target_multisource_mcts.csv", index=False)