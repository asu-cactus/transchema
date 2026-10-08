import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_3.csv", index_col=0)

# Normalize df2 column order to match others for clarity (not strictly necessary)
df2 = df2[['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

# For each source, group by SCHOOL_YEAR and count rows (using ULCS_NO as a non-null column)
df0_agg = df0.groupby('SCHOOL_YEAR', dropna=False).agg({ 'ULCS_NO': 'count' }).rename(columns={'ULCS_NO': 'ULCS_NO'}).reset_index()
df1_agg = df1.groupby('SCHOOL_YEAR', dropna=False).agg({ 'ULCS_NO': 'count' }).rename(columns={'ULCS_NO': 'INCIDENT_TYPE'}).reset_index()
df2_agg = df2.groupby('SCHOOL_YEAR', dropna=False).agg({ 'ULCS_NO': 'count' }).rename(columns={'ULCS_NO': 'INCIDENT_COUNT'}).reset_index()
df3_agg = df3.groupby('SCHOOL_YEAR', dropna=False).agg({ 'ULCS_NO': 'count' }).rename(columns={'ULCS_NO': 'SCHOOL_ID'}).reset_index()

# Join all aggregated dataframes on SCHOOL_YEAR
df_joined = df0_agg.merge(df1_agg, on='SCHOOL_YEAR', how='outer')
df_joined = df_joined.merge(df2_agg, on='SCHOOL_YEAR', how='outer')
df_joined = df_joined.merge(df3_agg, on='SCHOOL_YEAR', how='outer')

# Fill any missing counts with 0 and convert to int
df_joined = df_joined.fillna(0)
df_joined['ULCS_NO'] = df_joined['ULCS_NO'].astype(int)
df_joined['INCIDENT_TYPE'] = df_joined['INCIDENT_TYPE'].astype(int)
df_joined['INCIDENT_COUNT'] = df_joined['INCIDENT_COUNT'].astype(int)
df_joined['SCHOOL_ID'] = df_joined['SCHOOL_ID'].astype(int)

# Ensure SCHOOL_YEAR is string type
df_joined['SCHOOL_YEAR'] = df_joined['SCHOOL_YEAR'].astype(str)

# Reorder columns to match target schema
df_joined = df_joined[['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

# Write output
df_joined.to_csv("autopipeline-benchmarks/github-pipelines/length4_27/target_multisource_mcts.csv", index=False)