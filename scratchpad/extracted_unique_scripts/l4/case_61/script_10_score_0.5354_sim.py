import pandas as pd

def clean_int_column(s):
    return pd.to_numeric(s.astype(str).str.replace(r'\s+', '', regex=True).str.replace(' ', '', regex=False), errors='coerce').astype('Int64')

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_61/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_61/training_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_61/training_2.csv', index_col=0)
df3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_61/training_3.csv', index_col=0)

for df in [df0, df1, df2, df3]:
    df['N.°'] = clean_int_column(df['N.°'])
    df['Municipio'] = clean_int_column(df['Municipio'])
    df['Departamento'] = clean_int_column(df['Departamento'])
    df['Población cabecera'] = clean_int_column(df['Población cabecera'])
    df['Población resto'] = df['Población resto'].astype(str).str.strip()
    df['Población Total'] = clean_int_column(df['Población Total'])

df_merged = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_grouped = df_merged.groupby('Población resto', dropna=False, as_index=False).agg({
    'N.°': 'first',
    'Municipio': 'first',
    'Departamento': 'first',
    'Población cabecera': 'first',
    'Población Total': 'first'
})

df_grouped = df_grouped[['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']]

df_grouped.to_csv('autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv', index=False)