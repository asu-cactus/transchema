import pandas as pd

def main():
    # File paths
    paths = [
        'autopipeline-benchmarks/github-pipelines/length4_27/test_0.csv',
        'autopipeline-benchmarks/github-pipelines/length4_27/test_1.csv',
        'autopipeline-benchmarks/github-pipelines/length4_27/test_2.csv',
        'autopipeline-benchmarks/github-pipelines/length4_27/test_3.csv'
    ]

    dfs = []
    for i, path in enumerate(paths):
        # Read CSV ignoring first numeric index column
        df = pd.read_csv(path, index_col=0)

        # Standardize column order to target schema:
        # Target schema order: ['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']
        # Source schemas:
        # Source 0 and 1 and 3: ['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']
        # Source 2: ['ULCS_NO', 'SCHOOL_ID', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'INCIDENT_COUNT']

        # Fix column order if needed, and apply INCIDENT_TYPE transformation:
        if i != 2:
            # For sources 0,1,3
            # Columns: ULCS_NO, SCHOOL_YEAR, INCIDENT_TYPE, INCIDENT_COUNT, SCHOOL_ID
            # Reorder columns to target schema order and fix INCIDENT_TYPE
            df = df[['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']].copy()

            # Replace INCIDENT_TYPE values by ULCS_NO integer value
            df['INCIDENT_TYPE'] = df['ULCS_NO'].astype(int)
        else:
            # For source 2
            # ['ULCS_NO', 'SCHOOL_ID', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'INCIDENT_COUNT']
            # Reorder + transform
            df = df[['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']].copy()

            # Replace INCIDENT_TYPE by ULCS_NO integer value
            df['INCIDENT_TYPE'] = df['ULCS_NO'].astype(int)

        # Ensure correct dtypes as per target schema:
        df['SCHOOL_YEAR'] = df['SCHOOL_YEAR'].astype(str)
        df['ULCS_NO'] = df['ULCS_NO'].astype(int)
        df['INCIDENT_TYPE'] = df['INCIDENT_TYPE'].astype(int)
        df['INCIDENT_COUNT'] = df['INCIDENT_COUNT'].astype(int)
        df['SCHOOL_ID'] = df['SCHOOL_ID'].astype(int)

        dfs.append(df)

    # Concatenate (union) all source dfs
    result = pd.concat(dfs, ignore_index=True)

    # Write output CSV (without index)
    output_path = 'autopipeline-benchmarks/github-pipelines/length4_27/target_multisource_cot.csv'
    result.to_csv(output_path, index=False)

if __name__ == "__main__":
    main()