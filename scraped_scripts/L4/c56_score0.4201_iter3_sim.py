import pandas as pd

def normalize_incident_type(s):
    s = s.strip().upper()
    s = s.replace(" ", "_").replace("-", "_").replace("&", "AND")
    s = ''.join(c for c in s if c.isalnum() or c == '_')
    return s

def encode_incident_types(series):
    unique_types = sorted(series.unique())
    mapping = {v: i for i, v in enumerate(unique_types)}
    return series.map(mapping), mapping

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_56/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_56/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_56/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_56/training_3.csv", index_col=0)

for df in [df0, df1, df2, df3]:
    df['INCIDENT_TYPE'] = df['INCIDENT_TYPE'].astype(str).map(normalize_incident_type)

g0 = df0.groupby(['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'SCHOOL_ID'], as_index=False)['INCIDENT_COUNT'].sum()
g1 = df1.groupby(['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'SCHOOL_ID'], as_index=False)['INCIDENT_COUNT'].sum()
g2 = df2.groupby(['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'SCHOOL_ID'], as_index=False)['INCIDENT_COUNT'].sum()
g3 = df3.groupby(['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'SCHOOL_ID'], as_index=False)['INCIDENT_COUNT'].sum()

union_df = pd.concat([g0, g1, g2, g3], ignore_index=True)

final_group = union_df.groupby(['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'SCHOOL_ID'], as_index=False)['INCIDENT_COUNT'].sum()

final_group['SCHOOL_YEAR'] = final_group['SCHOOL_YEAR'].astype(str)

final_group['ULCS_NO'] = final_group['ULCS_NO'].astype(int)

# Encode INCIDENT_TYPE as integer codes
final_group['INCIDENT_TYPE'], _ = encode_incident_types(final_group['INCIDENT_TYPE'])

final_group['INCIDENT_COUNT'] = final_group['INCIDENT_COUNT'].astype(int)
final_group['SCHOOL_ID'] = final_group['SCHOOL_ID'].astype(int)

final_group = final_group[['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

final_group.to_csv("autopipeline-benchmarks/github-pipelines/length4_56/target_multisource_mcts.csv", index=False)