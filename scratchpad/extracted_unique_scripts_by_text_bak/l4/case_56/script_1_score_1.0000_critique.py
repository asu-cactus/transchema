import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_56/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_56/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_56/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_56/training_3.csv", index_col=0)

# UNION all source tables
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Ensure correct types
df_all['SCHOOL_YEAR'] = df_all['SCHOOL_YEAR'].astype(str)
df_all['ULCS_NO'] = df_all['ULCS_NO'].astype(int)
df_all['INCIDENT_TYPE'] = df_all['INCIDENT_TYPE'].astype(str)  # keep as string for counting
df_all['SCHOOL_ID'] = df_all['SCHOOL_ID'].astype(int)
df_all['INCIDENT_COUNT'] = pd.to_numeric(df_all['INCIDENT_COUNT'], errors='coerce').fillna(0).astype(int)

# Group by SCHOOL_YEAR and aggregate
df_grouped = df_all.groupby('SCHOOL_YEAR', as_index=False).agg({
    'ULCS_NO': 'count',          # count rows per year
    'INCIDENT_TYPE': 'count',   # count rows per year (same as ULCS_NO)
    'INCIDENT_COUNT': 'sum',    # sum of incident counts per year
    'SCHOOL_ID': 'count'        # count rows per year (same as ULCS_NO)
})

# Rename columns to match target schema exactly
df_grouped = df_grouped[['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_56/target_multisource_mcts.csv", index=False)