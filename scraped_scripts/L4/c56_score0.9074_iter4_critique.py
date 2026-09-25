import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_56/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_56/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_56/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_56/training_3.csv", index_col=0)

# Concatenate all source tables (UNION)
df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Normalize INCIDENT_TYPE strings to uppercase with underscores (to unify variants)
df['INCIDENT_TYPE'] = df['INCIDENT_TYPE'].str.upper().str.replace(r'[^A-Z0-9]', '_', regex=True)

# Ensure correct types
df['SCHOOL_YEAR'] = df['SCHOOL_YEAR'].astype(str)
df['ULCS_NO'] = df['ULCS_NO'].astype(int)
df['INCIDENT_COUNT'] = df['INCIDENT_COUNT'].astype(int)
df['SCHOOL_ID'] = df['SCHOOL_ID'].astype(int)

# Group by SCHOOL_YEAR and aggregate as per plan
result = df.groupby('SCHOOL_YEAR').agg(
    ULCS_NO=pd.NamedAgg(column='ULCS_NO', aggfunc=lambda x: x.nunique()),
    INCIDENT_TYPE=pd.NamedAgg(column='INCIDENT_TYPE', aggfunc=lambda x: x.nunique()),
    INCIDENT_COUNT=pd.NamedAgg(column='INCIDENT_COUNT', aggfunc='sum'),
    SCHOOL_ID=pd.NamedAgg(column='SCHOOL_ID', aggfunc=lambda x: x.nunique())
).reset_index()

# Write output with exact target schema and column order
result = result[['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_56/target_multisource_mcts.csv", index=False)