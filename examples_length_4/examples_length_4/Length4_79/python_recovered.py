import pandas as pd

def main():
    # List of source CSV file paths
    source_files = [
        "autopipeline-benchmarks/github-pipelines/length4_79/test_0.csv",
        "autopipeline-benchmarks/github-pipelines/length4_79/test_1.csv",
        "autopipeline-benchmarks/github-pipelines/length4_79/test_2.csv",
        "autopipeline-benchmarks/github-pipelines/length4_79/test_3.csv",
        "autopipeline-benchmarks/github-pipelines/length4_79/test_4.csv",
    ]

    # Read and collect all source dataframes
    dfs = []
    for file_path in source_files:
        df = pd.read_csv(file_path, index_col=0)
        dfs.append(df)

    # Concatenate all source dataframes (union)
    combined_df = pd.concat(dfs, ignore_index=True)

    # Ensure correct dtypes based on target schema
    combined_df['hero'] = combined_df['hero'].astype(str)
    combined_df['disadvantage'] = combined_df['disadvantage'].astype(float)
    combined_df['winrate'] = combined_df['winrate'].astype(float)
    combined_df['matches'] = combined_df['matches'].astype(int)

    # Output CSV file path
    output_path = "autopipeline-benchmarks/github-pipelines/length4_79/target_multisource_cot.csv"

    # Write to CSV with header and default index
    combined_df.to_csv(output_path, index=False)

if __name__ == "__main__":
    main()