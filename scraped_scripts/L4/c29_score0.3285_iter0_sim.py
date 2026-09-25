import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_3.csv", index_col=0)

def normalize_columns(df):
    df = df.copy()
    df.columns = df.columns.str.strip()
    if 'SCHOOL_ID' in df.columns and df['SCHOOL_ID'].dtype != 'int64':
        df['SCHOOL_ID'] = pd.to_numeric(df['SCHOOL_ID'], errors='coerce').fillna(0).astype(int)
    if 'ULCS_NO' in df.columns and df['ULCS_NO'].dtype != 'int64':
        df['ULCS_NO'] = pd.to_numeric(df['ULCS_NO'], errors='coerce').fillna(0).astype(int)
    if 'SCHOOL_YEAR' in df.columns:
        # Convert SCHOOL_YEAR to integer by extracting the last two digits of the second year if format like "2014-2015"
        def convert_year(y):
            if isinstance(y, str) and '-' in y:
                parts = y.split('-')
                try:
                    return int(parts[1][-2:])
                except:
                    return pd.NA
            try:
                return int(y)
            except:
                return pd.NA
        df['SCHOOL_YEAR'] = df['SCHOOL_YEAR'].apply(convert_year).astype('Int64')
    if 'INCIDENT_TYPE' in df.columns:
        df['INCIDENT_TYPE'] = df['INCIDENT_TYPE'].astype(str).str.upper().str.replace(r'[^A-Z0-9 ]', '', regex=True).str.strip()
        # Map INCIDENT_TYPE strings to integers by factorizing
        df['INCIDENT_TYPE'] = pd.factorize(df['INCIDENT_TYPE'])[0] + 1
    if 'INCIDENT_COUNT' in df.columns:
        df['INCIDENT_COUNT'] = pd.to_numeric(df['INCIDENT_COUNT'], errors='coerce').fillna(0).astype(int)
    return df[['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

df0n = normalize_columns(df0)
df1n = normalize_columns(df1)
df2n = normalize_columns(df2)
df3n = normalize_columns(df3)

df_all = pd.concat([df0n, df1n, df2n, df3n], ignore_index=True)

result = df_all.groupby(['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'SCHOOL_ID'], dropna=False, as_index=False)['INCIDENT_COUNT'].sum()
result = result.astype({'ULCS_NO': 'int64', 'SCHOOL_YEAR': 'int64', 'INCIDENT_TYPE': 'int64', 'INCIDENT_COUNT': 'int64', 'SCHOOL_ID': 'int64'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_29/target_multisource_mcts.csv", index=False)