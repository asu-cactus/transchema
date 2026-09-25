import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_3.csv", index_col=0)

def normalize_columns(df):
    df = df.copy()
    df.columns = df.columns.str.upper()
    if 'INCIDENT_COUNT' not in df.columns:
        df['INCIDENT_COUNT'] = 0
    # Normalize INCIDENT_TYPE: strip and uppercase
    df['INCIDENT_TYPE'] = df['INCIDENT_TYPE'].str.strip().str.upper()
    # Unify known variants in INCIDENT_TYPE
    df['INCIDENT_TYPE'] = df['INCIDENT_TYPE'].replace({
        'ASSAULT': 'ASSAULTS',
        'DRUG AND ALCOHOL OFFENSES': 'DRUGS & ALCOHOL OFFENSE',
        'DRUG AND ALCOHOL OFFENSE': 'DRUGS & ALCOHOL OFFENSE',
        'DRUGS & ALCOHOL OFFENSES': 'DRUGS & ALCOHOL OFFENSE',
    })
    # Convert SCHOOL_YEAR to int (take first year)
    def year_to_int(y):
        if isinstance(y, str) and '-' in y:
            return int(y.split('-')[0])
        try:
            return int(y)
        except:
            return pd.NA
    df['SCHOOL_YEAR'] = df['SCHOOL_YEAR'].apply(year_to_int)
    # Convert types
    df['ULCS_NO'] = pd.to_numeric(df['ULCS_NO'], errors='coerce').astype('Int64')
    df['SCHOOL_ID'] = pd.to_numeric(df['SCHOOL_ID'], errors='coerce').astype('Int64')
    df['INCIDENT_COUNT'] = pd.to_numeric(df['INCIDENT_COUNT'], errors='coerce').fillna(0).astype(int)
    df['INCIDENT_TYPE'] = df['INCIDENT_TYPE'].astype(str)
    return df[['INCIDENT_TYPE', 'ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_COUNT', 'SCHOOL_ID']]

df0n = normalize_columns(df0)
df1n = normalize_columns(df1)
df2n = normalize_columns(df2)
df3n = normalize_columns(df3)

# UNION all normalized dataframes
df_all = pd.concat([df0n, df1n, df2n, df3n], ignore_index=True)

# GROUP BY the leftmost columns and sum INCIDENT_COUNT
df_grouped = df_all.groupby(
    ['INCIDENT_TYPE', 'ULCS_NO', 'SCHOOL_YEAR', 'SCHOOL_ID'],
    dropna=False,
    as_index=False
).agg({'INCIDENT_COUNT': 'sum'})

# Reorder columns to match target schema exactly
df_grouped = df_grouped[['INCIDENT_TYPE', 'ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_COUNT', 'SCHOOL_ID']]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_28/target_multisource_mcts.csv", index=False)