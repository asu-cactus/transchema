import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_3.csv", index_col=0)

df2 = df2[['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df['SCHOOL_YEAR'] = df['SCHOOL_YEAR'].astype(str)
df['ULCS_NO'] = pd.to_numeric(df['ULCS_NO'], errors='coerce').astype('Int64')
df['INCIDENT_TYPE'] = pd.to_numeric(df['INCIDENT_TYPE'], errors='coerce').astype('Int64')
df['INCIDENT_COUNT'] = pd.to_numeric(df['INCIDENT_COUNT'], errors='coerce').astype('Int64')
df['SCHOOL_ID'] = pd.to_numeric(df['SCHOOL_ID'], errors='coerce').astype('Int64')

df = df[['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_27/target_multisource_mcts.csv", index=False)