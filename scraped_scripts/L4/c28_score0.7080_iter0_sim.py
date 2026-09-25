import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

def convert_school_year(s):
    if pd.isna(s):
        return None
    if isinstance(s, int):
        return s
    s = str(s)
    if '-' in s:
        parts = s.split('-')
        for p in parts:
            if p.isdigit() and len(p) == 4:
                return int(p)
    try:
        return int(s)
    except:
        return None

df['SCHOOL_YEAR'] = df['SCHOOL_YEAR'].apply(convert_school_year)

df['INCIDENT_TYPE'] = df['INCIDENT_TYPE'].str.upper().str.strip()

df['ULCS_NO'] = pd.to_numeric(df['ULCS_NO'], errors='coerce').astype('Int64')
df['SCHOOL_ID'] = pd.to_numeric(df['SCHOOL_ID'], errors='coerce').astype('Int64')
df['INCIDENT_COUNT'] = pd.to_numeric(df['INCIDENT_COUNT'], errors='coerce').fillna(0).astype(int)

grouped = df.groupby('INCIDENT_TYPE', dropna=False).agg({
    'ULCS_NO': 'max',
    'SCHOOL_YEAR': 'max',
    'INCIDENT_COUNT': 'sum',
    'SCHOOL_ID': 'max'
}).reset_index()

grouped = grouped.rename(columns={
    'INCIDENT_TYPE': 'INCIDENT_TYPE',
    'ULCS_NO': 'ULCS_NO',
    'SCHOOL_YEAR': 'SCHOOL_YEAR',
    'INCIDENT_COUNT': 'INCIDENT_COUNT',
    'SCHOOL_ID': 'SCHOOL_ID'
})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_28/target_multisource_mcts.csv", index=False)