import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_3.csv", index_col=0)

# UNION all source tables
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Normalize data types
df_all['INCIDENT_TYPE'] = df_all['INCIDENT_TYPE'].astype(str).str.upper()  # normalize case
df_all['ULCS_NO'] = pd.to_numeric(df_all['ULCS_NO'], errors='coerce').astype('Int64')
df_all['SCHOOL_ID'] = pd.to_numeric(df_all['SCHOOL_ID'], errors='coerce').astype('Int64')
df_all['INCIDENT_COUNT'] = pd.to_numeric(df_all['INCIDENT_COUNT'], errors='coerce').fillna(0).astype(int)

# Convert SCHOOL_YEAR to integer by extracting first year
def extract_year(s):
    try:
        return int(s)
    except:
        if isinstance(s, str) and '-' in s:
            return int(s.split('-')[0])
        return pd.NA

df_all['SCHOOL_YEAR'] = df_all['SCHOOL_YEAR'].apply(extract_year).astype('Int64')

# Group by INCIDENT_TYPE only
grouped = df_all.groupby('INCIDENT_TYPE', dropna=False, as_index=False).agg({
    'ULCS_NO': 'min',
    'SCHOOL_YEAR': 'min',
    'INCIDENT_COUNT': 'sum',
    'SCHOOL_ID': 'min'
})

# Reorder columns to match target schema
grouped = grouped[['INCIDENT_TYPE', 'ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_COUNT', 'SCHOOL_ID']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_28/target_multisource_mcts.csv", index=False)