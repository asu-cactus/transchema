import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_all['INCIDENT_TYPE'] = df_all['INCIDENT_TYPE'].str.upper().str.strip()
df_all['ULCS_NO'] = df_all['ULCS_NO'].astype(int)
df_all['SCHOOL_YEAR'] = df_all['SCHOOL_YEAR'].str.extract(r'(\d{4})').astype(int)
df_all['INCIDENT_COUNT'] = df_all['INCIDENT_COUNT'].astype(int)
df_all['SCHOOL_ID'] = df_all['SCHOOL_ID'].astype(int)

df_all = df_all[['INCIDENT_TYPE', 'ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_COUNT', 'SCHOOL_ID']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_28/target_multisource_mcts.csv", index=False)