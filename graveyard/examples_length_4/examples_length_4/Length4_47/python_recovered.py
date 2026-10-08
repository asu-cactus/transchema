import pandas as pd

def main():
    # File paths
    path0 = 'autopipeline-benchmarks/github-pipelines/length4_47/test_0.csv'
    path1 = 'autopipeline-benchmarks/github-pipelines/length4_47/test_1.csv'
    path2 = 'autopipeline-benchmarks/github-pipelines/length4_47/test_2.csv'
    path3 = 'autopipeline-benchmarks/github-pipelines/length4_47/test_3.csv'
    output_path = 'autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_cot.csv'

    # Load source files with index_col=0 to ignore first numeric index column
    source0 = pd.read_csv(path0, index_col=0)
    source1 = pd.read_csv(path1, index_col=0)
    source2 = pd.read_csv(path2, index_col=0)
    source3 = pd.read_csv(path3, index_col=0)

    # Union source0 and source2 as they have same schema (WarID, WarShortName, WarType)
    union_0_2 = pd.concat([source0, source2], ignore_index=True)

    # Remove duplicates if any (if needed) - but the problem doesn't say duplicates exist
    # union_0_2 = union_0_2.drop_duplicates(subset=['WarID'])

    # Prepare source1 and source3 with only relevant columns for joining:
    # source1 has IsIntervention
    s1 = source1[['WarID', 'IsIntervention']].drop_duplicates(subset=['WarID'])

    # source3 has IsInternational
    s3 = source3[['WarID', 'IsInternational']].drop_duplicates(subset=['WarID'])

    # Join union_0_2 with s1 on WarID to add IsIntervention
    merged = union_0_2.merge(s1, on='WarID', how='left')

    # Join the result with s3 on WarID to add IsInternational
    merged = merged.merge(s3, on='WarID', how='left')

    # Fill missing IsIntervention and IsInternational with 0, convert to int
    merged['IsIntervention'] = merged['IsIntervention'].fillna(0).astype(int)
    merged['IsInternational'] = merged['IsInternational'].fillna(0).astype(int)

    # Ensure WarID is integer type (it should be if from sources)
    merged['WarID'] = merged['WarID'].astype(int)

    # For WarShortName and WarType in target examples, they are integers,
    # but in sources WarShortName contains strings. Need conversion:
    # From examples, WarShortName in target is integer, same as WarID in example,
    # but source WarShortName is descriptive text (string).
    # The examples show WarShortName as integer equal to WarID.
    # So we can assign WarShortName = WarID as integer.

    merged['WarShortName'] = merged['WarID']

    # WarType: from source is integer already (check dtype)
    merged['WarType'] = merged['WarType'].astype(int)

    # Create final dataframe with target schema and order columns accordingly:
    target_df = merged[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

    # Save to output csv
    target_df.to_csv(output_path, index=False)

if __name__ == "__main__":
    main()