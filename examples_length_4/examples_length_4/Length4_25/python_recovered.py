import pandas as pd

def main():
    # Source file paths
    source_files = [
        "autopipeline-benchmarks/github-pipelines/length4_25/test_0.csv",
        "autopipeline-benchmarks/github-pipelines/length4_25/test_1.csv",
        "autopipeline-benchmarks/github-pipelines/length4_25/test_2.csv",
        "autopipeline-benchmarks/github-pipelines/length4_25/test_3.csv"
    ]

    # Read all source files into list of DataFrames
    dfs = []
    for file in source_files:
        df = pd.read_csv(file, index_col=0)
        dfs.append(df)

    # Concatenate all dataframes (union)
    combined_df = pd.concat(dfs, ignore_index=True)

    # Transformations:
    # Convert 'datetime' string -> integer by converting to datetime and taking ordinal (days since 0001-01-01)
    combined_df['datetime'] = pd.to_datetime(combined_df['datetime'], format='%Y-%m-%d', errors='coerce')
    # Fill NaT with some default or drop (should not happen normally)
    combined_df = combined_df.dropna(subset=['datetime'])
    combined_df['datetime'] = combined_df['datetime'].apply(lambda x: x.toordinal())

    # Convert 'station' string to categorical codes (integer). This gives zero-based codes; add 1 to start at 1 if preferred
    combined_df['station'] = combined_df['station'].astype('category').cat.codes + 1

    # Convert 'obs_type' string to categorical integer codes
    combined_df['obs_type'] = combined_df['obs_type'].astype('category').cat.codes + 1

    # Convert obs_value float to integer by rounding
    combined_df['obs_value'] = combined_df['obs_value'].round().astype(int)

    # Convert TMAX_F float to integer by rounding
    combined_df['TMAX_F'] = combined_df['TMAX_F'].round().astype(int)

    # Ensure month is integer
    combined_df['month'] = combined_df['month'].astype(int)

    # country_code as string (already should be)
    combined_df['country_code'] = combined_df['country_code'].astype(str)

    # Reorder columns to match target schema order:
    # ['country_code', 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'month']
    combined_df = combined_df[['country_code', 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'month']]

    # Write to target CSV
    target_path = "autopipeline-benchmarks/github-pipelines/length4_25/target_multisource_cot.csv"
    combined_df.to_csv(target_path, index=False)

if __name__ == "__main__":
    main()