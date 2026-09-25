import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_3.csv", index_col=0)

def normalize_incident_type(df):
    return df.assign(INCIDENT_TYPE=df['INCIDENT_TYPE'].str.upper().str.strip())

s0 = normalize_incident_type(s0)
s1 = normalize_incident_type(s1)
s2 = normalize_incident_type(s2)
s3 = normalize_incident_type(s3)

s2 = s2[['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

union_result = pd.concat([s0, s1, s3], ignore_index=True)

merged = pd.merge(union_result, s2, on=['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'SCHOOL_ID'], how='outer', suffixes=('_left', '_right'))

merged['INCIDENT_COUNT_left'] = merged['INCIDENT_COUNT_left'].fillna(0)
merged['INCIDENT_COUNT_right'] = merged['INCIDENT_COUNT_right'].fillna(0)
merged['INCIDENT_COUNT'] = merged['INCIDENT_COUNT_left'] + merged['INCIDENT_COUNT_right']

result = merged[['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

result['ULCS_NO'] = result['ULCS_NO'].astype(int)
result['SCHOOL_YEAR'] = result['SCHOOL_YEAR'].astype(str).str.extract(r'(\d{4})').astype(int)
result['INCIDENT_TYPE'] = result['INCIDENT_TYPE'].str.upper().str.strip()
result['INCIDENT_COUNT'] = result['INCIDENT_COUNT'].astype(int)
result['SCHOOL_ID'] = result['SCHOOL_ID'].astype(int)

result = result.groupby(['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'SCHOOL_ID'], as_index=False).agg({'INCIDENT_COUNT':'sum'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_29/target_multisource_mcts.csv", index=False)