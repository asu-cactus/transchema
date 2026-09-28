import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_3.csv", index_col=0)

def normalize_incident_type(s):
    return s.str.upper().str.replace(r'[^A-Z0-9 ]', '', regex=True).str.strip()

for df in [df0, df1, df2, df3]:
    df['INCIDENT_TYPE'] = normalize_incident_type(df['INCIDENT_TYPE'])
    df['SCHOOL_YEAR'] = df['SCHOOL_YEAR'].astype(str).str.extract(r'(\d{4})').astype(int)
    df['ULCS_NO'] = df['ULCS_NO'].astype(int)
    df['SCHOOL_ID'] = df['SCHOOL_ID'].astype(int)
    df['INCIDENT_COUNT'] = pd.to_numeric(df['INCIDENT_COUNT'], errors='coerce').fillna(0).astype(int)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

grouped = df_all.groupby(['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'SCHOOL_ID'], as_index=False)['INCIDENT_COUNT'].sum()

grouped['INCIDENT_TYPE'] = grouped['INCIDENT_TYPE'].astype(int, errors='ignore')
if grouped['INCIDENT_TYPE'].dtype != 'int64':
    # Map unique incident types to integers
    unique_types = sorted(grouped['INCIDENT_TYPE'].unique())
    type_map = {v: i for i, v in enumerate(unique_types, start=1)}
    grouped['INCIDENT_TYPE'] = grouped['INCIDENT_TYPE'].map(type_map).astype(int)

grouped = grouped[['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_29/target_multisource_mcts.csv", index=False)