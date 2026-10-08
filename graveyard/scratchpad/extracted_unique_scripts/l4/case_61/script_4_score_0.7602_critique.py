import pandas as pd

def clean_int_column(s):
    return pd.to_numeric(s.astype(str).str.replace(r'\s+', '', regex=True).str.replace(' ', '', regex=False), errors='coerce').astype('Int64')

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_61/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_61/training_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_61/training_2.csv', index_col=0)
df3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_61/training_3.csv', index_col=0)

for df in [df0, df1, df2, df3]:
    df['N.°'] = clean_int_column(df['N.°'])
    # Municipio and Departamento are string columns in source, but target expects integer.
    # The source examples show these as strings (names), so we must encode them as integers.
    # We will create consistent integer encoding across all dfs by concatenating and factorizing.
    df['Población cabecera'] = clean_int_column(df['Población cabecera'])
    df['Población resto'] = df['Población resto'].astype(str).str.strip()
    df['Población Total'] = clean_int_column(df['Población Total'])

# Concatenate all to encode Municipio and Departamento consistently
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Factorize Municipio and Departamento to integers (starting from 1)
df_all['Municipio'] = pd.factorize(df_all['Municipio'])[0] + 1
df_all['Departamento'] = pd.factorize(df_all['Departamento'])[0] + 1

# Now group by the key columns: 'N.°', 'Municipio', 'Departamento'
# Aggregations: take first for 'Población resto', 'Población cabecera', 'Población Total'
df_grouped = df_all.groupby(['N.°', 'Municipio', 'Departamento'], dropna=False, as_index=False).agg({
    'Población resto': 'first',
    'Población cabecera': 'first',
    'Población Total': 'first'
})

# Reorder columns to match target schema: ['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']
df_grouped = df_grouped[['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']]

df_grouped.to_csv('autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv', index=False)