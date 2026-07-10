import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_3.csv", index_col=0)

# Concatenate all sources (UNION)
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Normalize columns
df_all['ULCS_NO'] = df_all['ULCS_NO'].astype(int)

# SCHOOL_YEAR: extract 4-digit year and convert to int
# But target SCHOOL_YEAR is integer like 60, 61, 57, so keep as is (max per ULCS_NO)
df_all['SCHOOL_YEAR'] = df_all['SCHOOL_YEAR'].astype(str).str.extract(r'(\d{4})').astype(int)

# Normalize INCIDENT_TYPE strings: uppercase, remove non-alphanumeric
df_all['INCIDENT_TYPE'] = df_all['INCIDENT_TYPE'].astype(str).str.upper().str.replace(r'[^A-Z0-9]', '', regex=True)

df_all['SCHOOL_ID'] = df_all['SCHOOL_ID'].astype(int)
df_all['INCIDENT_COUNT'] = pd.to_numeric(df_all['INCIDENT_COUNT'], errors='coerce').fillna(0).astype(int)

# Map INCIDENT_TYPE to integer codes
incident_type_map = {v: k for k, v in enumerate(sorted(df_all['INCIDENT_TYPE'].unique()), start=1)}
df_all['INCIDENT_TYPE'] = df_all['INCIDENT_TYPE'].map(incident_type_map).astype(int)

# Group by ULCS_NO and aggregate
df_grouped = df_all.groupby('ULCS_NO', as_index=False).agg({
    'SCHOOL_YEAR': 'max',
    'INCIDENT_TYPE': 'max',
    'INCIDENT_COUNT': 'sum',
    'SCHOOL_ID': 'max'
})

# Reorder columns to match target schema
df_grouped = df_grouped[['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_29/target_multisource_mcts.csv", index=False)