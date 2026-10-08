import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_3.csv", index_col=0)

# UNION all source tables
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Ensure SCHOOL_YEAR is string type
df_all['SCHOOL_YEAR'] = df_all['SCHOOL_YEAR'].astype(str)

# GROUP BY SCHOOL_YEAR and count rows for each column as per target examples
result = df_all.groupby('SCHOOL_YEAR', dropna=False).agg({
    'ULCS_NO': 'count',
    'INCIDENT_TYPE': 'count',
    'INCIDENT_COUNT': 'count',
    'SCHOOL_ID': 'count'
}).reset_index()

# Rename columns to match target schema exactly
result = result[['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

# Convert columns to integer type as in target schema
result['ULCS_NO'] = result['ULCS_NO'].astype(int)
result['INCIDENT_TYPE'] = result['INCIDENT_TYPE'].astype(int)
result['INCIDENT_COUNT'] = result['INCIDENT_COUNT'].astype(int)
result['SCHOOL_ID'] = result['SCHOOL_ID'].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_27/target_multisource_mcts.csv", index=False)