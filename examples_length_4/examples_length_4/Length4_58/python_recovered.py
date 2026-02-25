import pandas as pd

def main():
    # Define file paths
    source_files = [
        'autopipeline-benchmarks/github-pipelines/length4_58/test_0.csv',
        'autopipeline-benchmarks/github-pipelines/length4_58/test_1.csv',
        'autopipeline-benchmarks/github-pipelines/length4_58/test_2.csv',
        'autopipeline-benchmarks/github-pipelines/length4_58/test_3.csv',
    ]
    
    # Read all source dataframes with index_col=0 to ignore the first index column
    source_dfs = [pd.read_csv(fp, index_col=0) for fp in source_files]
    
    # Concatenate all source dataframes (UNION ALL)
    combined_df = pd.concat(source_dfs, ignore_index=True)
    
    # Fill NaN in 'TransTo' column with 0 (since target examples mostly 0, mapping NaN to 0)
    combined_df['TransTo'] = combined_df['TransTo'].fillna(0).astype(int)
    
    # Ensure 'WarNum' as integer
    combined_df['WarNum'] = combined_df['WarNum'].astype(int)
    
    # Select and reorder columns to match target schema (although they already match)
    target_columns = ['WarNum', 'TransTo']
    result_df = combined_df[target_columns]

    # Write the result to the target path
    result_df.to_csv('autopipeline-benchmarks/github-pipelines/length4_58/target_multisource_cot.csv', index=False)

if __name__ == "__main__":
    main()