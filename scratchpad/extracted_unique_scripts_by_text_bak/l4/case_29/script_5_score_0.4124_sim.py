import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_all['SCHOOL_YEAR'] = df_all['SCHOOL_YEAR'].astype(str).str.extract(r'(\d{4})').astype(int)

df_all['INCIDENT_TYPE'] = df_all['INCIDENT_TYPE'].str.upper().str.replace(r'[^A-Z0-9 ]', '', regex=True).str.strip()

df_grouped = df_all.groupby(['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'SCHOOL_ID'], as_index=False)['INCIDENT_COUNT'].sum()

df_grouped['ULCS_NO'] = df_grouped['ULCS_NO'].astype(int)
df_grouped['SCHOOL_YEAR'] = df_grouped['SCHOOL_YEAR'].astype(int)
df_grouped['INCIDENT_TYPE'] = df_grouped['INCIDENT_TYPE'].astype(str)
df_grouped['INCIDENT_COUNT'] = df_grouped['INCIDENT_COUNT'].astype(int)
df_grouped['SCHOOL_ID'] = df_grouped['SCHOOL_ID'].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_29/target_multisource_mcts.csv", index=False)