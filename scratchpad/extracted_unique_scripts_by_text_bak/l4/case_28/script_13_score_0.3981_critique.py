import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_3.csv", index_col=0)

# UNION all source tables
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Normalize INCIDENT_TYPE: uppercase and strip
df_all['INCIDENT_TYPE'] = df_all['INCIDENT_TYPE'].astype(str).str.upper().str.strip()

# Convert ULCS_NO and SCHOOL_ID to integer (nullable Int64)
df_all['ULCS_NO'] = pd.to_numeric(df_all['ULCS_NO'], errors='coerce').astype('Int64')
df_all['SCHOOL_ID'] = pd.to_numeric(df_all['SCHOOL_ID'], errors='coerce').astype('Int64')

# Convert INCIDENT_COUNT to int, fill NaN with 0
df_all['INCIDENT_COUNT'] = pd.to_numeric(df_all['INCIDENT_COUNT'], errors='coerce').fillna(0).astype(int)

# SCHOOL_YEAR: convert string to categorical codes (int)
df_all['SCHOOL_YEAR'] = df_all['SCHOOL_YEAR'].astype(str).str.strip()
df_all['SCHOOL_YEAR'], _ = pd.factorize(df_all['SCHOOL_YEAR'])
df_all['SCHOOL_YEAR'] = df_all['SCHOOL_YEAR'].astype('Int64')

# Group by INCIDENT_TYPE, ULCS_NO, SCHOOL_YEAR
# Aggregate sum of INCIDENT_COUNT and take first SCHOOL_ID per group
grouped = df_all.groupby(['INCIDENT_TYPE', 'ULCS_NO', 'SCHOOL_YEAR'], dropna=False, as_index=False).agg({
    'INCIDENT_COUNT': 'sum',
    'SCHOOL_ID': 'first'
})

# Ensure correct dtypes
grouped['INCIDENT_TYPE'] = grouped['INCIDENT_TYPE'].astype(str)
grouped['ULCS_NO'] = grouped['ULCS_NO'].astype('Int64')
grouped['SCHOOL_YEAR'] = grouped['SCHOOL_YEAR'].astype('Int64')
grouped['INCIDENT_COUNT'] = grouped['INCIDENT_COUNT'].astype(int)
grouped['SCHOOL_ID'] = grouped['SCHOOL_ID'].astype('Int64')

# Reorder columns to match target schema
grouped = grouped[['INCIDENT_TYPE', 'ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_COUNT', 'SCHOOL_ID']]

# Write output
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_28/target_multisource_mcts.csv", index=False)