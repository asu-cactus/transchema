import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_29/training_3.csv", index_col=0)

def normalize_string_column(s):
    return s.str.upper().str.replace(r'[^A-Z0-9 ]', '', regex=True).str.strip()

for df in [df0, df1, df2, df3]:
    df['INCIDENT_TYPE'] = normalize_string_column(df['INCIDENT_TYPE'])
    df['SCHOOL_YEAR'] = df['SCHOOL_YEAR'].astype(str).str.strip()
    df['ULCS_NO'] = df['ULCS_NO'].astype(int)
    df['SCHOOL_ID'] = df['SCHOOL_ID'].astype(int)
    df['INCIDENT_COUNT'] = pd.to_numeric(df['INCIDENT_COUNT'], errors='coerce').fillna(0).astype(int)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Map SCHOOL_YEAR strings to integer codes
unique_school_years = sorted(df_all['SCHOOL_YEAR'].unique())
school_year_map = {v: i for i, v in enumerate(unique_school_years, start=1)}
df_all['SCHOOL_YEAR'] = df_all['SCHOOL_YEAR'].map(school_year_map).astype(int)

# Map INCIDENT_TYPE strings to integer codes
unique_incident_types = sorted(df_all['INCIDENT_TYPE'].unique())
incident_type_map = {v: i for i, v in enumerate(unique_incident_types, start=1)}
df_all['INCIDENT_TYPE'] = df_all['INCIDENT_TYPE'].map(incident_type_map).astype(int)

grouped = df_all.groupby(['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'SCHOOL_ID'], as_index=False)['INCIDENT_COUNT'].sum()

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_29/target_multisource_mcts.csv", index=False)