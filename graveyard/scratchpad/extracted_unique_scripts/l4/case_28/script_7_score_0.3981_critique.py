import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df['INCIDENT_TYPE'] = df['INCIDENT_TYPE'].str.upper()

# Extract the first 4 digits of SCHOOL_YEAR and convert to int
df['SCHOOL_YEAR'] = df['SCHOOL_YEAR'].str[:4].astype(int)

agg = df.groupby(['INCIDENT_TYPE', 'ULCS_NO', 'SCHOOL_YEAR'], as_index=False).agg({
    'INCIDENT_COUNT': 'sum',
    'SCHOOL_ID': 'max'
})

agg['INCIDENT_COUNT'] = agg['INCIDENT_COUNT'].astype(int)
agg['SCHOOL_ID'] = agg['SCHOOL_ID'].astype(int)
agg['ULCS_NO'] = agg['ULCS_NO'].astype(int)
agg['SCHOOL_YEAR'] = agg['SCHOOL_YEAR'].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_28/target_multisource_mcts.csv", index=False)