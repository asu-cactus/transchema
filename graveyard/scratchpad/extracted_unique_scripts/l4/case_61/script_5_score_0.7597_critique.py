import pandas as pd

def clean_number_column(col):
    return col.str.replace(r'\s+', '', regex=True).str.replace(' ', '', regex=False).str.replace(',', '').astype(int)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_61/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    df['Población cabecera'] = clean_number_column(df['Población cabecera'])
    df['Población resto'] = clean_number_column(df['Población resto'])
    df['Población Total'] = clean_number_column(df['Población Total'])
    df['N.°'] = df['N.°'].astype(int)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

# Convert Municipio and Departamento to categorical codes (integers)
df_all['Municipio'] = df_all['Municipio'].astype('category').cat.codes + 1  # +1 to avoid zero if needed
df_all['Departamento'] = df_all['Departamento'].astype('category').cat.codes + 1

# Format Población resto as string with spaces as thousands separators
df_all['Población resto'] = df_all['Población resto'].map('{:,}'.format).str.replace(',', ' ')

# Format population columns as integers (already int), no need to format as string except Población resto
# But target schema shows Población resto as string, others as int

# Reorder columns as per target schema
df_all = df_all[['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv", index=False)