import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df['INCIDENT_TYPE'] = df['INCIDENT_TYPE'].str.upper().str.strip()
df['ULCS_NO'] = df['ULCS_NO'].astype(int)
df['SCHOOL_YEAR'] = df['SCHOOL_YEAR'].str[:4].astype(int)
df['INCIDENT_COUNT'] = df['INCIDENT_COUNT'].astype(int)
df['SCHOOL_ID'] = df['SCHOOL_ID'].astype(int)

df = df[['INCIDENT_TYPE', 'ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_COUNT', 'SCHOOL_ID']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_28/target_multisource_mcts.csv", index=False)