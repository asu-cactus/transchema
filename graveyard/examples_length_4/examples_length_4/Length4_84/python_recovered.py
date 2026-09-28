import pandas as pd

def main():
    # Source file paths
    source_paths = [
        "autopipeline-benchmarks/github-pipelines/length4_84/test_0.csv",
        "autopipeline-benchmarks/github-pipelines/length4_84/test_1.csv",
        "autopipeline-benchmarks/github-pipelines/length4_84/test_2.csv",
        "autopipeline-benchmarks/github-pipelines/length4_84/test_3.csv",
        "autopipeline-benchmarks/github-pipelines/length4_84/test_4.csv",
    ]

    # List to store individual source DataFrames
    dfs = []
    for path in source_paths:
        df = pd.read_csv(path, index_col=0)
        dfs.append(df)

    # Concatenate all source DataFrames vertically (union)
    combined_df = pd.concat(dfs, ignore_index=True)

    # Select & reorder columns according to target schema (excluding "Unnamed: 1")
    # Target schema: ['age_grp' (string), 'Count' (float), 'Notes' (string), 'Rate' (float), 'Statistics' (string)]
    # The sources have these columns plus an extra unnamed column (ignored by index_col=0)
    target_cols = ['age_grp', 'Count', 'Notes', 'Rate', 'Statistics']
    combined_df = combined_df[target_cols]

    # Enforce correct dtypes from target schema
    combined_df['age_grp'] = combined_df['age_grp'].astype(str)
    combined_df['Notes'] = combined_df['Notes'].astype(str)
    combined_df['Statistics'] = combined_df['Statistics'].astype(str)
    combined_df['Count'] = pd.to_numeric(combined_df['Count'], errors='coerce')
    combined_df['Rate'] = pd.to_numeric(combined_df['Rate'], errors='coerce')

    # Replace any string "nan" caused by astype(str) on NaNs back to actual NaN
    for col in ['age_grp', 'Notes', 'Statistics']:
        combined_df[col] = combined_df[col].replace({'nan': pd.NA})

    # Save to the target csv file
    output_path = "autopipeline-benchmarks/github-pipelines/length4_84/target_multisource_cot.csv"
    combined_df.to_csv(output_path, index=False)

if __name__ == "__main__":
    main()