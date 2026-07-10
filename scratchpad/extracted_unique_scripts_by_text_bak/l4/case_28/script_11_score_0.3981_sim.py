import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df['INCIDENT_TYPE'] = df['INCIDENT_TYPE'].str.upper().str.strip()

df['SCHOOL_YEAR'] = df['SCHOOL_YEAR'].astype(str).str.extract(r'(\d{4})').astype(int)

df_grouped = df.groupby(['INCIDENT_TYPE', 'ULCS_NO', 'SCHOOL_YEAR', 'SCHOOL_ID'], as_index=False)['INCIDENT_COUNT'].sum()

df_grouped = df_grouped.rename(columns={'INCIDENT_COUNT': 'INCIDENT_COUNT'})

df_grouped = df_grouped.astype({
    'INCIDENT_TYPE': str,
    'ULCS_NO': int,
    'SCHOOL_YEAR': int,
    'INCIDENT_COUNT': int,
    'SCHOOL_ID': int
})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_28/target_multisource_mcts.csv", index=False)