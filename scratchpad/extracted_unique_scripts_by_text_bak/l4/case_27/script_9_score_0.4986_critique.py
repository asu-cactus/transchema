import pandas as pd

# Read sources with index_col=0 as instructed
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_3.csv", index_col=0)

# Align s2 columns order to match others: ['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']
s2 = s2[['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

# Concatenate all sources
combined = pd.concat([s0, s1, s2, s3], ignore_index=True)

# Convert SCHOOL_YEAR to string
combined['SCHOOL_YEAR'] = combined['SCHOOL_YEAR'].astype(str)

# Convert ULCS_NO and SCHOOL_ID to int
combined['ULCS_NO'] = combined['ULCS_NO'].astype(int)
combined['SCHOOL_ID'] = combined['SCHOOL_ID'].astype(int)

# Fill missing INCIDENT_COUNT with 0 and convert to int
combined['INCIDENT_COUNT'] = combined['INCIDENT_COUNT'].fillna(0).astype(int)

# Encode INCIDENT_TYPE strings to integers to match target schema
combined['INCIDENT_TYPE'] = combined['INCIDENT_TYPE'].astype(str)
combined['INCIDENT_TYPE'] = combined['INCIDENT_TYPE'].str.strip()  # remove leading/trailing spaces if any
combined['INCIDENT_TYPE'] = combined['INCIDENT_TYPE'].astype('category').cat.codes.astype(int)

# Group by the leftmost columns (SCHOOL_YEAR, ULCS_NO, INCIDENT_TYPE, SCHOOL_ID) and sum INCIDENT_COUNT
result = combined.groupby(['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'SCHOOL_ID'], as_index=False).agg({'INCIDENT_COUNT': 'sum'})

# Reorder columns to match target schema: ['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']
result = result[['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

# Write to output CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_27/target_multisource_mcts.csv", index=False)