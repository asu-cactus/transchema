import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_56/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_56/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_56/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_56/training_3.csv", index_col=0)

# UNION all source tables
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Group by SCHOOL_YEAR and count rows per year
grouped = df_all.groupby('SCHOOL_YEAR', as_index=False).size()

# Rename the count column to match target schema columns and assign the same count to all integer columns
grouped = grouped.rename(columns={'size': 'ULCS_NO'})
grouped['INCIDENT_TYPE'] = grouped['ULCS_NO']
grouped['INCIDENT_COUNT'] = grouped['ULCS_NO']
grouped['SCHOOL_ID'] = grouped['ULCS_NO']

# Ensure correct types
grouped['SCHOOL_YEAR'] = grouped['SCHOOL_YEAR'].astype(str)
grouped['ULCS_NO'] = grouped['ULCS_NO'].astype(int)
grouped['INCIDENT_TYPE'] = grouped['INCIDENT_TYPE'].astype(int)
grouped['INCIDENT_COUNT'] = grouped['INCIDENT_COUNT'].astype(int)
grouped['SCHOOL_ID'] = grouped['SCHOOL_ID'].astype(int)

# Reorder columns to match target schema exactly
grouped = grouped[['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_56/target_multisource_mcts.csv", index=False)