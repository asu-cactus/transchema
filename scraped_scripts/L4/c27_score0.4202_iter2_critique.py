import pandas as pd

def clean_incident_type(df):
    df = df.copy()
    # Normalize INCIDENT_TYPE strings: uppercase alphanumeric only, no spaces or special chars
    df['INCIDENT_TYPE'] = df['INCIDENT_TYPE'].str.upper().str.replace(r'[^A-Z0-9]', '', regex=True)
    return df

def main():
    path0 = "autopipeline-benchmarks/github-pipelines/length4_27/training_0.csv"
    path1 = "autopipeline-benchmarks/github-pipelines/length4_27/training_1.csv"
    path2 = "autopipeline-benchmarks/github-pipelines/length4_27/training_2.csv"
    path3 = "autopipeline-benchmarks/github-pipelines/length4_27/training_3.csv"
    out_path = "autopipeline-benchmarks/github-pipelines/length4_27/target_multisource_mcts.csv"

    # Read all sources with index_col=0 to ignore the first column (index)
    df0 = pd.read_csv(path0, index_col=0)
    df1 = pd.read_csv(path1, index_col=0)
    df2 = pd.read_csv(path2, index_col=0)
    df3 = pd.read_csv(path3, index_col=0)

    # Normalize INCIDENT_TYPE strings in all sources for consistent keys
    df0 = clean_incident_type(df0)
    df1 = clean_incident_type(df1)
    df2 = clean_incident_type(df2)
    df3 = clean_incident_type(df3)

    # Reorder columns in df2 to match others (ULCS_NO, SCHOOL_YEAR, INCIDENT_TYPE, INCIDENT_COUNT, SCHOOL_ID)
    df2 = df2[['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

    # Concatenate all sources (UNION)
    df_all = pd.concat([df0, df1, df2, df3], ignore_index=True, sort=False)

    # Group by leftmost columns of target schema (non-float, unique): SCHOOL_YEAR, ULCS_NO, INCIDENT_TYPE, SCHOOL_ID
    # Aggregate sum of INCIDENT_COUNT
    df_grouped = df_all.groupby(['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'SCHOOL_ID'], as_index=False)['INCIDENT_COUNT'].sum()

    # Map INCIDENT_TYPE strings to integers consistently
    unique_incidents = sorted(df_grouped['INCIDENT_TYPE'].unique())
    incident_map = {v: i+1 for i, v in enumerate(unique_incidents)}
    df_grouped['INCIDENT_TYPE'] = df_grouped['INCIDENT_TYPE'].map(incident_map)

    # Cast columns to target types
    df_grouped['SCHOOL_YEAR'] = df_grouped['SCHOOL_YEAR'].astype(str)
    df_grouped['ULCS_NO'] = df_grouped['ULCS_NO'].astype(int)
    df_grouped['INCIDENT_TYPE'] = df_grouped['INCIDENT_TYPE'].astype(int)
    df_grouped['INCIDENT_COUNT'] = df_grouped['INCIDENT_COUNT'].astype(int)
    df_grouped['SCHOOL_ID'] = df_grouped['SCHOOL_ID'].astype(int)

    # Write output
    df_grouped.to_csv(out_path, index=False)

if __name__ == "__main__":
    main()