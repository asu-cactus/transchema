import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_3.csv", index_col=0)

def normalize_incident_type(s):
    return s.str.strip().str.upper().str.replace(r'[^A-Z0-9 ]', '', regex=True).str.replace(r'\s+', ' ', regex=True)

for df in [df0, df1, df2, df3]:
    df['INCIDENT_TYPE'] = normalize_incident_type(df['INCIDENT_TYPE'])
    df['ULCS_NO'] = df['ULCS_NO'].astype(int)
    df['SCHOOL_YEAR'] = df['SCHOOL_YEAR'].astype(str).str.extract(r'(\d{4})').astype(int)
    df['INCIDENT_COUNT'] = df['INCIDENT_COUNT'].astype(int)
    df['SCHOOL_ID'] = df['SCHOOL_ID'].astype(int)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_all = df_all[['INCIDENT_TYPE', 'ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_COUNT', 'SCHOOL_ID']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_28/target_multisource_mcts.csv", index=False)