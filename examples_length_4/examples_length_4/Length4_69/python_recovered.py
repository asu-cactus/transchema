import pandas as pd

def main():
    # File paths for source data
    path_source_0 = 'autopipeline-benchmarks/github-pipelines/length4_69/test_0.csv'
    path_source_1 = 'autopipeline-benchmarks/github-pipelines/length4_69/test_1.csv'
    path_source_2 = 'autopipeline-benchmarks/github-pipelines/length4_69/test_2.csv'

    # Load source tables with index_col=0 to ignore the numerical index column
    df0 = pd.read_csv(path_source_0, index_col=0)
    df1 = pd.read_csv(path_source_1, index_col=0)
    df2 = pd.read_csv(path_source_2, index_col=0)

    # Join all source tables on 'user_id'
    # Use outer join to keep all user_ids and NaNs as in target examples
    df_01 = pd.merge(df0, df1, on='user_id', how='outer')
    df_all = pd.merge(df_01, df2, on='user_id', how='outer')

    # Ensure columns are ordered as target schema
    # Target schema: ['user_id': int, 'year_school': str, 'floor': str, 'party': str, 'libcon': str, 'fav_music': str]
    target_columns = ['user_id', 'year_school', 'floor', 'party', 'libcon', 'fav_music']

    # Select only these columns (some might have NaNs)
    df_result = df_all[target_columns]

    # Convert column types to match target
    # user_id: integer, the rest are strings (floor may have NaN which will be float NaN, so convert carefully)
    df_result['user_id'] = df_result['user_id'].astype('Int64')  # nullable integer type to allow NaNs if any
    
    # For string columns, convert dtype but preserve NaN
    for col in ['year_school', 'floor', 'party', 'libcon', 'fav_music']:
        df_result[col] = df_result[col].astype('string')

    # Write to CSV
    output_path = 'autopipeline-benchmarks/github-pipelines/length4_69/target_multisource_cot.csv'
    df_result.to_csv(output_path, index=False)

if __name__ == "__main__":
    main()