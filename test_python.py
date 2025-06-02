import pandas as pd

def load_source(filename):
    # Load CSV ignoring the first index column by using index_col=0
    # We only keep columns ['code', 'name'] which are the 2nd and 3rd columns (after index)
    df = pd.read_csv(filename, index_col=0)
    # Ensure we keep only columns code and name as per schema, no extra columns
    df = df[['code', 'name']]
    return df

def main():
    # Define source file paths
    source_files = {
        'Source9_5_0':  "autopipeline-benchmarks/github-pipelines/length9_5/test_0.csv",
        'Source9_5_1':  "autopipeline-benchmarks/github-pipelines/length9_5/test_1.csv",
        'Source9_5_2':  "autopipeline-benchmarks/github-pipelines/length9_5/test_2.csv",
        'Source9_5_3':  "autopipeline-benchmarks/github-pipelines/length9_5/test_3.csv",
        'Source9_5_4':  "autopipeline-benchmarks/github-pipelines/length9_5/test_4.csv",
        'Source9_5_5':  "autopipeline-benchmarks/github-pipelines/length9_5/test_5.csv",
        'Source9_5_6':  "autopipeline-benchmarks/github-pipelines/length9_5/test_6.csv",
        'Source9_5_7':  "autopipeline-benchmarks/github-pipelines/length9_5/test_7.csv",
        'Source9_5_8':  "autopipeline-benchmarks/github-pipelines/length9_5/test_8.csv",
        'Source9_5_9':  "autopipeline-benchmarks/github-pipelines/length9_5/test_9.csv",
        'Source9_5_10': "autopipeline-benchmarks/github-pipelines/length9_5/test_10.csv",
    }

    # Load all sources into a dictionary of DataFrames
    sources = {}
    for key, path in source_files.items():
        df = load_source(path)
        # Verify schema correctness: columns should be ['code', 'name']
        assert list(df.columns) == ['code', 'name'], f"Schema mismatch in {key}"
        sources[key] = df

    # According to operation_history:
    # 1) UNION : ['Source9_5_7', 'Source9_5_2']
    union1 = pd.concat([sources['Source9_5_7'], sources['Source9_5_2']], ignore_index=True)

    # 2) UNION : ['Source9_5_0', 'Source9_5_1', 'Source9_5_3', 'Source9_5_4', 'Source9_5_5',
    #             'Source9_5_6', 'Source9_5_8', 'Source9_5_9', 'Source9_5_10']
    union2_sources = ['Source9_5_0', 'Source9_5_1', 'Source9_5_3', 'Source9_5_4', 'Source9_5_5',
                     'Source9_5_6', 'Source9_5_8', 'Source9_5_9', 'Source9_5_10']
    union2 = pd.concat([sources[src] for src in union2_sources], ignore_index=True)

    # Final union of the two unions (combining all sources)
    final_df = pd.concat([union1, union2], ignore_index=True)

    # Validate final schema matches target schema exactly
    # Target schema: ['code', 'name']
    assert list(final_df.columns) == ['code', 'name'], "Final dataframe schema mismatch"

    # Remove potential duplicate rows to keep closer to target, but not explicitly stated as required
    final_df = final_df.drop_duplicates(ignore_index=True)

    # Sort by 'code' ascending as good practice (optional)
    final_df = final_df.sort_values(by='code').reset_index(drop=True)

    # Save to target path
    target_path = "autopipeline-benchmarks/github-pipelines/length9_5/target_multisource.csv"
    final_df.to_csv(target_path, index=False)

if __name__ == '__main__':
    main()