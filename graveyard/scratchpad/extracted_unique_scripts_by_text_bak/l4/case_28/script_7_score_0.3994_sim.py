import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_grouped = df_all.groupby(
    ['INCIDENT_TYPE', 'ULCS_NO', 'SCHOOL_YEAR', 'SCHOOL_ID'], dropna=False, as_index=False
).agg({'INCIDENT_COUNT': 'sum'})

df_grouped['ULCS_NO'] = df_grouped['ULCS_NO'].astype(int)
df_grouped['SCHOOL_YEAR'] = df_grouped['SCHOOL_YEAR'].astype(str)
df_grouped['INCIDENT_TYPE'] = df_grouped['INCIDENT_TYPE'].astype(str)
df_grouped['SCHOOL_ID'] = df_grouped['SCHOOL_ID'].astype(int)
df_grouped['INCIDENT_COUNT'] = df_grouped['INCIDENT_COUNT'].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_28/target_multisource_mcts.csv", index=False)