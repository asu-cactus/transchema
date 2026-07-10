import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_3.csv", index_col=0)

# UNION all sources
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Normalize SCHOOL_YEAR: extract first 4 digits (start year)
df_all['SCHOOL_YEAR'] = df_all['SCHOOL_YEAR'].astype(str).str.extract(r'(\d{4})')[0]

# Normalize INCIDENT_TYPE strings: uppercase, remove non-alphanumeric except space, strip
df_all['INCIDENT_TYPE'] = df_all['INCIDENT_TYPE'].astype(str).str.upper().str.replace(r'[^A-Z0-9 ]', '', regex=True).str.strip()

# Map SCHOOL_YEAR to integer codes (categorical codes)
df_all['SCHOOL_YEAR'] = df_all['SCHOOL_YEAR'].astype('category').cat.codes

# Map INCIDENT_TYPE to integer codes (categorical codes)
df_all['INCIDENT_TYPE'] = df_all['INCIDENT_TYPE'].astype('category').cat.codes

# Ensure ULCS_NO and SCHOOL_ID are int
df_all['ULCS_NO'] = df_all['ULCS_NO'].astype(int)
df_all['SCHOOL_ID'] = df_all['SCHOOL_ID'].astype(int)

# Aggregate sum of INCIDENT_COUNT grouped by keys
df_grouped = df_all.groupby(['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'SCHOOL_ID'], as_index=False)['INCIDENT_COUNT'].sum()

# Cast columns to int as per target schema
df_grouped['ULCS_NO'] = df_grouped['ULCS_NO'].astype(int)
df_grouped['SCHOOL_YEAR'] = df_grouped['SCHOOL_YEAR'].astype(int)
df_grouped['INCIDENT_TYPE'] = df_grouped['INCIDENT_TYPE'].astype(int)
df_grouped['INCIDENT_COUNT'] = df_grouped['INCIDENT_COUNT'].astype(int)
df_grouped['SCHOOL_ID'] = df_grouped['SCHOOL_ID'].astype(int)

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_29/target_multisource_mcts.csv", index=False)