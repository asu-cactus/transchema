import pandas as pd

def normalize_incident_type(df):
    df = df.copy()
    df['INCIDENT_TYPE'] = df['INCIDENT_TYPE'].str.upper().str.replace(r'[^A-Z0-9]', '', regex=True)
    mapping = {v: k for k, v in enumerate(sorted(df['INCIDENT_TYPE'].unique()), 1)}
    df['INCIDENT_TYPE'] = df['INCIDENT_TYPE'].map(mapping)
    return df, mapping

def main():
    path0 = "autopipeline-benchmarks/github-pipelines/length4_27/training_0.csv"
    path1 = "autopipeline-benchmarks/github-pipelines/length4_27/training_1.csv"
    path2 = "autopipeline-benchmarks/github-pipelines/length4_27/training_2.csv"
    path3 = "autopipeline-benchmarks/github-pipelines/length4_27/training_3.csv"
    out_path = "autopipeline-benchmarks/github-pipelines/length4_27/target_multisource_mcts.csv"

    df0 = pd.read_csv(path0, index_col=0)
    df1 = pd.read_csv(path1, index_col=0)
    df2 = pd.read_csv(path2, index_col=0)
    df3 = pd.read_csv(path3, index_col=0)

    # Normalize INCIDENT_TYPE strings in all sources to uppercase alphanumeric only for consistent join keys
    def clean_incident_type(df):
        df = df.copy()
        df['INCIDENT_TYPE'] = df['INCIDENT_TYPE'].str.upper().str.replace(r'[^A-Z0-9]', '', regex=True)
        return df

    df0 = clean_incident_type(df0)
    df1 = clean_incident_type(df1)
    df2 = clean_incident_type(df2)
    df3 = clean_incident_type(df3)

    # Join Source0 and Source2 on ULCS_NO, SCHOOL_YEAR, INCIDENT_TYPE, SCHOOL_ID
    join_cols = ['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'SCHOOL_ID']
    df_join = pd.merge(df0, df2, on=join_cols, suffixes=('_0', '_2'))

    # Sum INCIDENT_COUNT from both sides
    df_join['INCIDENT_COUNT'] = df_join['INCIDENT_COUNT_0'] + df_join['INCIDENT_COUNT_2']

    # Keep only join_cols + INCIDENT_COUNT
    df_join = df_join[join_cols + ['INCIDENT_COUNT']]

    # Union the joined result with Source1 and Source3 (which have same schema as Source0)
    df_all = pd.concat([df_join, df1, df3], ignore_index=True, sort=False)

    # Group by SCHOOL_YEAR, ULCS_NO, INCIDENT_TYPE, SCHOOL_ID and sum INCIDENT_COUNT
    df_grouped = df_all.groupby(['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'SCHOOL_ID'], as_index=False)['INCIDENT_COUNT'].sum()

    # Map INCIDENT_TYPE strings to integers consistently across all data
    # We already cleaned strings, now create a mapping from all unique INCIDENT_TYPE strings in all sources
    # But after join and concat, INCIDENT_TYPE is still string, so map to integer IDs
    # To do this, we need to re-derive mapping from all original sources combined

    # Collect all unique INCIDENT_TYPE strings from all sources before cleaning
    # But we only have cleaned strings now, so use df_all's INCIDENT_TYPE column
    unique_incidents = sorted(df_all['INCIDENT_TYPE'].unique())
    incident_map = {v: i+1 for i, v in enumerate(unique_incidents)}
    df_grouped['INCIDENT_TYPE'] = df_grouped['INCIDENT_TYPE'].map(incident_map)

    # Cast columns to target types
    df_grouped['SCHOOL_YEAR'] = df_grouped['SCHOOL_YEAR'].astype(str)
    df_grouped['ULCS_NO'] = df_grouped['ULCS_NO'].astype(int)
    df_grouped['INCIDENT_TYPE'] = df_grouped['INCIDENT_TYPE'].astype(int)
    df_grouped['INCIDENT_COUNT'] = df_grouped['INCIDENT_COUNT'].astype(int)
    df_grouped['SCHOOL_ID'] = df_grouped['SCHOOL_ID'].astype(int)

    df_grouped.to_csv(out_path, index=False)

if __name__ == "__main__":
    main()