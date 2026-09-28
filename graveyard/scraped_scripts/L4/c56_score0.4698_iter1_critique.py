import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_56/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_56/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_56/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_56/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_all['SCHOOL_YEAR'] = df_all['SCHOOL_YEAR'].astype(str)
df_all['ULCS_NO'] = pd.to_numeric(df_all['ULCS_NO'], errors='coerce').astype('Int64')
df_all['INCIDENT_TYPE'] = df_all['INCIDENT_TYPE'].astype(str)
df_all['INCIDENT_COUNT'] = pd.to_numeric(df_all['INCIDENT_COUNT'], errors='coerce').fillna(0).astype(int)
df_all['SCHOOL_ID'] = pd.to_numeric(df_all['SCHOOL_ID'], errors='coerce').astype('Int64')

# Factorize INCIDENT_TYPE to integer
df_all['INCIDENT_TYPE'], _ = pd.factorize(df_all['INCIDENT_TYPE'])

# Group by SCHOOL_YEAR and ULCS_NO, aggregate sums of INCIDENT_TYPE, INCIDENT_COUNT, SCHOOL_ID
df_grouped = df_all.groupby(['SCHOOL_YEAR', 'ULCS_NO'], as_index=False).agg({
    'INCIDENT_TYPE': 'sum',
    'INCIDENT_COUNT': 'sum',
    'SCHOOL_ID': 'sum'
})

# Reorder columns to match target schema
df_grouped = df_grouped[['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_56/target_multisource_mcts.csv", index=False)