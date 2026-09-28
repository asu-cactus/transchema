import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_28/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_all['INCIDENT_TYPE'] = df_all['INCIDENT_TYPE'].astype(str)
df_all['ULCS_NO'] = pd.to_numeric(df_all['ULCS_NO'], errors='coerce').astype('Int64')
df_all['SCHOOL_YEAR'] = df_all['SCHOOL_YEAR'].astype(str)
df_all['SCHOOL_ID'] = pd.to_numeric(df_all['SCHOOL_ID'], errors='coerce').astype('Int64')
df_all['INCIDENT_COUNT'] = pd.to_numeric(df_all['INCIDENT_COUNT'], errors='coerce').fillna(0).astype(int)

grouped = df_all.groupby(['INCIDENT_TYPE', 'ULCS_NO', 'SCHOOL_YEAR', 'SCHOOL_ID'], dropna=False, as_index=False)['INCIDENT_COUNT'].sum()

def try_int_year(s):
    try:
        return int(s)
    except:
        # try to parse school year like "2014-2015" to 2014
        if isinstance(s, str) and '-' in s:
            return int(s.split('-')[0])
        return pd.NA

grouped['SCHOOL_YEAR'] = grouped['SCHOOL_YEAR'].apply(try_int_year).astype('Int64')

grouped = grouped[['INCIDENT_TYPE', 'ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_COUNT', 'SCHOOL_ID']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_28/target_multisource_mcts.csv", index=False)