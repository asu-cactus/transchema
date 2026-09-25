import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_3.csv", index_col=0)

# Reorder columns in df2 to match others
df2 = df2[['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

# Concatenate all sources
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Normalize INCIDENT_TYPE strings: uppercase and remove non-alphanumeric characters
df_all['INCIDENT_TYPE'] = df_all['INCIDENT_TYPE'].astype(str).str.upper().str.replace(r'[^A-Z0-9]', '', regex=True)

# Ensure types for grouping and aggregation
df_all['SCHOOL_YEAR'] = df_all['SCHOOL_YEAR'].astype(str)
df_all['ULCS_NO'] = pd.to_numeric(df_all['ULCS_NO'], errors='coerce').astype('Int64')
df_all['SCHOOL_ID'] = pd.to_numeric(df_all['SCHOOL_ID'], errors='coerce').astype('Int64')
df_all['INCIDENT_COUNT'] = pd.to_numeric(df_all['INCIDENT_COUNT'], errors='coerce').fillna(0).astype(int)

# Group by SCHOOL_YEAR and aggregate counts as per plan
result = df_all.groupby('SCHOOL_YEAR', dropna=False).agg(
    ULCS_NO = ('ULCS_NO', 'nunique'),
    INCIDENT_TYPE = ('INCIDENT_TYPE', 'nunique'),
    SCHOOL_ID = ('SCHOOL_ID', 'nunique'),
    INCIDENT_COUNT = ('INCIDENT_COUNT', 'count')
).reset_index()

# Convert columns to match target schema types
result['ULCS_NO'] = result['ULCS_NO'].astype(int)
result['INCIDENT_TYPE'] = result['INCIDENT_TYPE'].astype(int)
result['SCHOOL_ID'] = result['SCHOOL_ID'].astype(int)
result['INCIDENT_COUNT'] = result['INCIDENT_COUNT'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_27/target_multisource_mcts.csv", index=False)