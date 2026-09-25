import pandas as pd

# Source file paths
source_paths = [
    'autopipeline-benchmarks/github-pipelines/length4_56/test_0.csv',
    'autopipeline-benchmarks/github-pipelines/length4_56/test_1.csv',
    'autopipeline-benchmarks/github-pipelines/length4_56/test_2.csv',
    'autopipeline-benchmarks/github-pipelines/length4_56/test_3.csv'
]

# Target columns and types
target_columns = ['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']
# Target schema: SCHOOL_YEAR: string, ULCS_NO: int, INCIDENT_TYPE: int, INCIDENT_COUNT: int, SCHOOL_ID:int

dfs = []
for path in source_paths:
    df = pd.read_csv(path, index_col=0)

    # Normalize columns - reorder to target. Source columns vary in order 
    # For source 3, order is ['ULCS_NO', 'SCHOOL_ID', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'INCIDENT_COUNT']
    # We rearrange columns to match target schema order.

    # 1. Rename columns to standard if needed (some incidence type values differ in case but column names are consistent)
    # Because all have the same column names except order, just reorder columns

    # Reorder columns; all source tables contain these columns but in different orders
    # Ensure all needed columns exist
    assert set(target_columns) == set(df.columns), f"Mismatch columns in {path}"

    df = df[target_columns]  # reorder columns to target order

    # Convert INCIDENT_TYPE column: target examples show INCIDENT_TYPE = ULCS_NO (integer)
    # So replace INCIDENT_TYPE by ULCS_NO values (convert to int)
    df['ULCS_NO'] = df['ULCS_NO'].astype(int)
    df['INCIDENT_TYPE'] = df['ULCS_NO']

    # Convert data types according to target
    df['SCHOOL_YEAR'] = df['SCHOOL_YEAR'].astype(str)
    df['ULCS_NO'] = df['ULCS_NO'].astype(int)
    df['INCIDENT_TYPE'] = df['INCIDENT_TYPE'].astype(int)
    df['INCIDENT_COUNT'] = df['INCIDENT_COUNT'].astype(int)
    df['SCHOOL_ID'] = df['SCHOOL_ID'].astype(int)

    dfs.append(df)

# Concatenate all source dataframes (union)
target_df = pd.concat(dfs, ignore_index=True)

# Write to CSV without the index column
target_df.to_csv('autopipeline-benchmarks/github-pipelines/length4_56/target_multisource_cot.csv', index=False)