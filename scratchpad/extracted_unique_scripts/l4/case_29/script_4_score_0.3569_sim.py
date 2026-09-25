import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_all['ULCS_NO'] = df_all['ULCS_NO'].astype(int)
df_all['SCHOOL_YEAR'] = df_all['SCHOOL_YEAR'].astype(str).str.extract(r'(\d{4})').astype(int)
df_all['INCIDENT_TYPE'] = df_all['INCIDENT_TYPE'].astype(str).str.upper().str.replace(r'[^A-Z0-9]', '', regex=True)
df_all['SCHOOL_ID'] = df_all['SCHOOL_ID'].astype(int)
df_all['INCIDENT_COUNT'] = pd.to_numeric(df_all['INCIDENT_COUNT'], errors='coerce').fillna(0).astype(int)

incident_type_map = {v: k for k, v in enumerate(sorted(df_all['INCIDENT_TYPE'].unique()), start=1)}
df_all['INCIDENT_TYPE'] = df_all['INCIDENT_TYPE'].map(incident_type_map).astype(int)

df_all = df_all[['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_29/target_multisource_mcts.csv", index=False)