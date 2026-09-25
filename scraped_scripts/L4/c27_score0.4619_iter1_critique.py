import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_27/training_3.csv", index_col=0)

# Reorder columns in df2 to match others
df2 = df2[['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

# UNION all source tables
df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Convert SCHOOL_YEAR to string
df['SCHOOL_YEAR'] = df['SCHOOL_YEAR'].astype(str)

# INCIDENT_TYPE is string in sources, but target expects integer.
# We will convert INCIDENT_TYPE to numeric by counting occurrences per group.
# So first, convert INCIDENT_TYPE to 1 for counting, or just sum counts later.
# But since target INCIDENT_TYPE is integer and values are similar to counts,
# we treat INCIDENT_TYPE as count of incidents per group (sum of 1 per row).
# So replace INCIDENT_TYPE with 1 for aggregation.
df['INCIDENT_TYPE'] = 1

# Convert other columns to numeric for aggregation
df['ULCS_NO'] = pd.to_numeric(df['ULCS_NO'], errors='coerce').astype('Int64')
df['INCIDENT_COUNT'] = pd.to_numeric(df['INCIDENT_COUNT'], errors='coerce').fillna(0).astype(int)
df['SCHOOL_ID'] = pd.to_numeric(df['SCHOOL_ID'], errors='coerce').astype('Int64')

# Group by SCHOOL_YEAR and ULCS_NO, aggregate sums of INCIDENT_TYPE, INCIDENT_COUNT, SCHOOL_ID
agg_df = df.groupby(['SCHOOL_YEAR', 'ULCS_NO'], as_index=False).agg({
    'INCIDENT_TYPE': 'sum',
    'INCIDENT_COUNT': 'sum',
    'SCHOOL_ID': 'sum'
})

# Ensure columns are in target schema order
agg_df = agg_df[['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_27/target_multisource_mcts.csv", index=False)