import pandas as pd

# Read sources with index_col=0 as instructed
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_3.csv", index_col=0)

def normalize_incident_type(df):
    return df.assign(INCIDENT_TYPE=df['INCIDENT_TYPE'].str.upper().str.strip())

# Normalize INCIDENT_TYPE in all sources
s0 = normalize_incident_type(s0)
s1 = normalize_incident_type(s1)
s2 = normalize_incident_type(s2)
s3 = normalize_incident_type(s3)

# Reorder s2 columns to match others
s2 = s2[['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

# Union all sources
union_df = pd.concat([s0, s1, s2, s3], ignore_index=True)

# Extract 4-digit year from SCHOOL_YEAR string and convert to int
union_df = union_df.assign(
    SCHOOL_YEAR=union_df['SCHOOL_YEAR'].astype(str).str.extract(r'(\d{4})')[0].astype(int)
)

# Group by keys and sum INCIDENT_COUNT
result = union_df.groupby(
    ['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'SCHOOL_ID'], as_index=False
).agg({'INCIDENT_COUNT': 'sum'})

# Ensure correct dtypes
result = result.astype({
    'ULCS_NO': int,
    'SCHOOL_YEAR': int,
    'INCIDENT_TYPE': str,
    'INCIDENT_COUNT': int,
    'SCHOOL_ID': int
})

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_29/target_multisource_mcts.csv", index=False)