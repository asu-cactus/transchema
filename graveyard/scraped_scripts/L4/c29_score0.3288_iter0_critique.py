import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_3.csv", index_col=0)

def normalize_school_year(df):
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
    return df['SCHOOL_YEAR'].apply(convert_year).astype('Int64')

def normalize_incident_type_str(s):
    # Uppercase, remove non-alphanumeric and spaces, strip
    return s.astype(str).str.upper().str.replace(r'[^A-Z0-9 ]', '', regex=True).str.strip()

# Normalize columns except INCIDENT_TYPE factorization
def normalize_columns_partial(df):
    df = df.copy()
    df.columns = df.columns.str.strip()
    if 'SCHOOL_ID' in df.columns and df['SCHOOL_ID'].dtype != 'int64':
        df['SCHOOL_ID'] = pd.to_numeric(df['SCHOOL_ID'], errors='coerce').fillna(0).astype(int)
    if 'ULCS_NO' in df.columns and df['ULCS_NO'].dtype != 'int64':
        df['ULCS_NO'] = pd.to_numeric(df['ULCS_NO'], errors='coerce').fillna(0).astype(int)
    if 'SCHOOL_YEAR' in df.columns:
        df['SCHOOL_YEAR'] = normalize_school_year(df)
    if 'INCIDENT_COUNT' in df.columns:
        df['INCIDENT_COUNT'] = pd.to_numeric(df['INCIDENT_COUNT'], errors='coerce').fillna(0).astype(int)
    return df

# Normalize all tables partially (except INCIDENT_TYPE factorization)
df0n = normalize_columns_partial(df0)
df1n = normalize_columns_partial(df1)
df2n = normalize_columns_partial(df2)
df3n = normalize_columns_partial(df3)

# Normalize INCIDENT_TYPE strings for all tables
df0n['INCIDENT_TYPE'] = normalize_incident_type_str(df0n['INCIDENT_TYPE'])
df1n['INCIDENT_TYPE'] = normalize_incident_type_str(df1n['INCIDENT_TYPE'])
df2n['INCIDENT_TYPE'] = normalize_incident_type_str(df2n['INCIDENT_TYPE'])
df3n['INCIDENT_TYPE'] = normalize_incident_type_str(df3n['INCIDENT_TYPE'])

# Combine all INCIDENT_TYPE strings to create a global mapping
all_incident_types = pd.concat([
    df0n['INCIDENT_TYPE'],
    df1n['INCIDENT_TYPE'],
    df2n['INCIDENT_TYPE'],
    df3n['INCIDENT_TYPE']
]).dropna().unique()

# Create a global mapping from INCIDENT_TYPE string to integer code starting from 1
incident_type_map = {v: i+1 for i, v in enumerate(sorted(all_incident_types))}

# Map INCIDENT_TYPE strings to integers using the global mapping
def map_incident_type(df):
    df = df.copy()
    df['INCIDENT_TYPE'] = df['INCIDENT_TYPE'].map(incident_type_map).fillna(0).astype(int)
    return df

df0n = map_incident_type(df0n)
df1n = map_incident_type(df1n)
df2n = map_incident_type(df2n)
df3n = map_incident_type(df3n)

# Concatenate all normalized tables
df_all = pd.concat([df0n, df1n, df2n, df3n], ignore_index=True)

# Group by the key columns and sum INCIDENT_COUNT
result = df_all.groupby(['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'SCHOOL_ID'], dropna=False, as_index=False)['INCIDENT_COUNT'].sum()

# Ensure all columns are int64 as per target schema
result = result.astype({'ULCS_NO': 'int64', 'SCHOOL_YEAR': 'int64', 'INCIDENT_TYPE': 'int64', 'INCIDENT_COUNT': 'int64', 'SCHOOL_ID': 'int64'})

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_29/target_multisource_mcts.csv", index=False)