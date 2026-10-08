import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_3.csv", index_col=0)

# Reorder columns of df2 to match others (ULCS_NO, SCHOOL_YEAR, INCIDENT_TYPE, INCIDENT_COUNT, SCHOOL_ID)
df2 = df2[['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

# Concatenate all sources (UNION)
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Normalize SCHOOL_YEAR to integer year (extract first 4-digit year)
df_all['SCHOOL_YEAR'] = df_all['SCHOOL_YEAR'].astype(str).str.extract(r'(\d{4})').astype(int)

# Normalize INCIDENT_TYPE strings: strip, lower, remove extra spaces for consistent mapping
df_all['INCIDENT_TYPE'] = df_all['INCIDENT_TYPE'].astype(str).str.strip().str.lower()

# Create a consistent mapping of INCIDENT_TYPE to integers
incident_type_map = {k: i+1 for i, k in enumerate(sorted(df_all['INCIDENT_TYPE'].unique()))}
df_all['INCIDENT_TYPE'] = df_all['INCIDENT_TYPE'].map(incident_type_map)

# Group by all columns except INCIDENT_COUNT, sum INCIDENT_COUNT
df_grouped = df_all.groupby(['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'SCHOOL_ID'], as_index=False)['INCIDENT_COUNT'].sum()

# Ensure all columns are int type as per target schema
df_grouped = df_grouped.astype({'ULCS_NO': int, 'SCHOOL_YEAR': int, 'INCIDENT_TYPE': int, 'INCIDENT_COUNT': int, 'SCHOOL_ID': int})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_29/target_multisource_mcts.csv", index=False)