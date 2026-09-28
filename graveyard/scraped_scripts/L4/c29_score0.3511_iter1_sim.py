import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_3.csv", index_col=0)

def normalize_columns(df):
    df = df.copy()
    # Standardize column order and names
    # Source 2 has SCHOOL_ID before SCHOOL_YEAR, reorder to match others
    if list(df.columns) == ['ULCS_NO', 'SCHOOL_ID', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'INCIDENT_COUNT']:
        df = df[['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]
    # Normalize INCIDENT_TYPE strings: uppercase and strip spaces
    df['INCIDENT_TYPE'] = df['INCIDENT_TYPE'].astype(str).str.upper().str.strip()
    # Normalize SCHOOL_YEAR strings: remove spaces
    df['SCHOOL_YEAR'] = df['SCHOOL_YEAR'].astype(str).str.strip()
    # Convert numeric columns to int if possible
    for col in ['ULCS_NO', 'INCIDENT_COUNT', 'SCHOOL_ID']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    # Convert SCHOOL_YEAR to int by extracting first 4 digits (e.g. "2014-2015" -> 2014)
    def year_to_int(y):
        try:
            return int(str(y)[:4])
        except:
            return pd.NA
    df['SCHOOL_YEAR'] = df['SCHOOL_YEAR'].apply(year_to_int)
    df['SCHOOL_YEAR'] = pd.to_numeric(df['SCHOOL_YEAR'], errors='coerce').fillna(0).astype(int)
    # Convert INCIDENT_TYPE to int by hashing consistently
    # Since target INCIDENT_TYPE is int, map unique INCIDENT_TYPE strings to unique ints
    return df

df0 = normalize_columns(df0)
df1 = normalize_columns(df1)
df2 = normalize_columns(df2)
df3 = normalize_columns(df3)

# Combine all unique INCIDENT_TYPE values from all dfs
all_incident_types = pd.Series(pd.concat([df0['INCIDENT_TYPE'], df1['INCIDENT_TYPE'], df2['INCIDENT_TYPE'], df3['INCIDENT_TYPE']]).unique())
incident_type_map = {v: i for i, v in enumerate(sorted(all_incident_types), 1)}

for df in [df0, df1, df2, df3]:
    df['INCIDENT_TYPE'] = df['INCIDENT_TYPE'].map(incident_type_map).fillna(0).astype(int)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_all = df_all[['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_29/target_multisource_mcts.csv", index=False)