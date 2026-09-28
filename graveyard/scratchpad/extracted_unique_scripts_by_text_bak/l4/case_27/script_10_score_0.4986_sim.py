import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_3.csv", index_col=0)

def normalize_incident_type(s):
    return s.str.upper().str.replace(r'[^A-Z0-9]', '', regex=True)

for df in [df0, df1, df2, df3]:
    df['INCIDENT_TYPE'] = normalize_incident_type(df['INCIDENT_TYPE'])

union_df = pd.concat([df0, df1, df2, df3], ignore_index=True)

grouped = union_df.groupby(['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'SCHOOL_ID'], as_index=False)['INCIDENT_COUNT'].sum()

grouped['ULCS_NO'] = grouped['ULCS_NO'].astype(int)
grouped['INCIDENT_TYPE'] = grouped['INCIDENT_TYPE'].astype(int, errors='ignore')
if grouped['INCIDENT_TYPE'].dtype != 'int64':
    # If conversion to int failed (likely because INCIDENT_TYPE is not numeric), try to convert by mapping unique strings to ints
    unique_types = pd.Series(grouped['INCIDENT_TYPE'].unique()).sort_values().reset_index(drop=True)
    type_to_int = {v: i for i, v in enumerate(unique_types)}
    grouped['INCIDENT_TYPE'] = grouped['INCIDENT_TYPE'].map(type_to_int).astype(int)

grouped['SCHOOL_ID'] = grouped['SCHOOL_ID'].astype(int)
grouped['INCIDENT_COUNT'] = grouped['INCIDENT_COUNT'].astype(int)

grouped = grouped[['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_27/target_multisource_mcts.csv", index=False)