import pandas as pd

def main():
    # Source file path
    source_0_path = 'autopipeline-benchmarks/github-pipelines/length4_67/test_0.csv'

    # Read source data with index_col=0 to ignore the first numerical index column
    source_0 = pd.read_csv(source_0_path, index_col=0)

    # Select columns needed for target and rename if necessary
    # In this case column names already match in case and spacing for 'Batsman on strike', 'overs', 'runs scored', 'extras'
    target_df = source_0[['Batsman on strike', 'overs', 'runs scored', 'extras']].copy()

    # Convert data types according to target schema
    # 'Batsman on strike': string (object in pandas)
    target_df['Batsman on strike'] = target_df['Batsman on strike'].astype(str)

    # 'overs': float
    target_df['overs'] = target_df['overs'].astype(float)

    # 'runs scored': integer
    target_df['runs scored'] = target_df['runs scored'].astype(int)

    # 'extras': integer
    target_df['extras'] = target_df['extras'].astype(int)

    # Write the result CSV without the index (drop the pandas index)
    output_path = 'autopipeline-benchmarks/github-pipelines/length4_67/target_multisource_cot.csv'
    target_df.to_csv(output_path, index=False)

if __name__ == "__main__":
    main()