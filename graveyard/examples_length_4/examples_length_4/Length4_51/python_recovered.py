import pandas as pd

def main():
    # Source files paths
    src_paths = [
        'autopipeline-benchmarks/github-pipelines/length4_51/test_0.csv',
        'autopipeline-benchmarks/github-pipelines/length4_51/test_1.csv',
        'autopipeline-benchmarks/github-pipelines/length4_51/test_2.csv',
        'autopipeline-benchmarks/github-pipelines/length4_51/test_3.csv'
    ]

    # Define full target columns and types as per target schema
    target_cols = [
        'Side',          # string
        'WarID',         # int
        'PolityID',      # int
        'StartYear',     # int
        'StartMonth',    # int
        'StartDay',      # int
        'EndYear',       # int
        'EndMonth',      # int
        'EndDay',        # int
        'IsInitiator',   # int
        'Outcome',       # int
        'Deaths',        # int
        'PolityName'     # int (encoded)
    ]

    # Load sources one by one, align columns, fill missing columns for union

    # Source0 columns: ['WarID', 'PolityID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']
    df0 = pd.read_csv(src_paths[0], index_col=0)

    # Source1 columns: ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']
    df1 = pd.read_csv(src_paths[1], index_col=0)
    # Add missing PolityName column with NaN for df1
    df1['PolityName'] = pd.NA

    # Source2 columns same as Source0 (with PolityName)
    df2 = pd.read_csv(src_paths[2], index_col=0)

    # Source3 columns same as Source0 (with PolityName)
    df3 = pd.read_csv(src_paths[3], index_col=0)

    # Concatenate all dataframes
    df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

    # Fill any missing PolityID with 0 or -1 for integer conversion (NaNs will prevent int conversion)
    df_all['PolityID'] = df_all['PolityID'].fillna(-1).astype(int)

    # For date fields, fill na with 0 and convert to int
    date_cols = ['StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay']
    for col in date_cols:
        df_all[col] = df_all[col].fillna(0).astype(int)

    # For integer columns with possible NaNs: IsInitiator, Outcome, Deaths
    int_columns = ['IsInitiator', 'Outcome', 'Deaths']
    for col in int_columns:
        df_all[col] = df_all[col].fillna(0).astype(int)

    # Side column as string (if any NaN fill with empty string)
    df_all['Side'] = df_all['Side'].fillna('').astype(str)

    # Handle PolityName encoding:
    # We need to convert string polity names to integers. For null or missing names, assign 0.
    # Use pandas factorize which returns numeric codes starting from 0.
    # We add 1 to ensure 0 reserved for missing (NaN) polity names.

    # Convert all NaN PolityName to string 'Unknown' for encoding separation or keep NaN and encode with fill
    polity_name_series = df_all['PolityName'].fillna('Unknown').astype(str)
    codes, uniques = pd.factorize(polity_name_series)
    # Map 'Unknown' to code 0 (we shift +1 so Unknown is 0)
    # But factorize codes start at 0 for first unique which will be 'Unknown'
    # So codes are already 0-based with 'Unknown' as code 0, so just keep as is
    df_all['PolityName'] = codes.astype(int)

    # Reorder columns to target schema order
    df_all = df_all[target_cols]

    # Save result to csv
    out_path = 'autopipeline-benchmarks/github-pipelines/length4_51/target_multisource_cot.csv'
    df_all.to_csv(out_path, index=False)

if __name__ == '__main__':
    main()