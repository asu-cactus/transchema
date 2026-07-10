import pandas as pd

# Read all source CSVs with index_col=0 to ignore the first numerical index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_3.csv", index_col=0)

# Normalize INCIDENT_TYPE strings to uppercase and remove non-alphanumeric characters for consistency
def normalize_incident_type(s):
    return s.str.upper().str.replace(r'[^A-Z0-9]', '', regex=True)

for df in [df0, df1, df2, df3]:
    df['INCIDENT_TYPE'] = normalize_incident_type(df['INCIDENT_TYPE'])

# Union all source tables
union_df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Group by SCHOOL_YEAR only
grouped = union_df.groupby('SCHOOL_YEAR', as_index=False).agg({
    'ULCS_NO': pd.Series.nunique,
    'INCIDENT_TYPE': pd.Series.nunique,
    'INCIDENT_COUNT': 'sum',
    'SCHOOL_ID': pd.Series.nunique
})

# Rename columns to match target schema exactly
grouped.columns = ['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']

# Cast columns to correct types
grouped['SCHOOL_YEAR'] = grouped['SCHOOL_YEAR'].astype(str)
grouped['ULCS_NO'] = grouped['ULCS_NO'].astype(int)
grouped['INCIDENT_TYPE'] = grouped['INCIDENT_TYPE'].astype(int)
grouped['INCIDENT_COUNT'] = grouped['INCIDENT_COUNT'].astype(int)
grouped['SCHOOL_ID'] = grouped['SCHOOL_ID'].astype(int)

# Write output CSV with exact target schema column order
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_27/target_multisource_mcts.csv", index=False)