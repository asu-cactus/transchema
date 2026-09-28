import pandas as pd

def clean_number_column(col):
    return col.astype(str).str.replace(r'\s', '', regex=True).str.replace(' ', '', regex=False).str.replace(',', '').astype(int)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_60/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    df['N.°'] = df['N.°'].astype(int)
    df['Municipio'] = df['Municipio'].astype(str)
    df['Departamento'] = df['Departamento'].astype(str)
    for col in ['Población cabecera', 'Población resto', 'Población Total']:
        df[col] = clean_number_column(df[col])
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

# The partial plan suggests PIVOT and GROUP_BY on Municipio.
# Since the source tables already have the target columns, and Municipio is unique per row,
# we just group by Municipio and aggregate numeric columns by sum or first as appropriate.

# Departamento is integer in target schema, but source has string names.
# We need to convert Departamento to integer.
# Since Departamento in source is string (e.g. "Norte de Santander"), but target expects integer,
# we must encode Departamento strings to integers consistently.

# Create a mapping from Departamento string to integer
departamento_map = {name: idx+1 for idx, name in enumerate(sorted(df_all['Departamento'].unique()))}
df_all['Departamento'] = df_all['Departamento'].map(departamento_map)

# Group by Municipio, aggregate:
# For 'N.°' and 'Departamento' take first (assuming Municipio unique)
# For population columns sum (in case duplicates)
agg_dict = {
    'N.°': 'first',
    'Departamento': 'first',
    'Población cabecera': 'sum',
    'Población resto': 'sum',
    'Población Total': 'sum'
}

df_grouped = df_all.groupby('Municipio', as_index=False).agg(agg_dict)

# Reorder columns to target schema order
df_grouped = df_grouped[['Municipio', 'N.°', 'Departamento', 'Población cabecera', 'Población resto', 'Población Total']]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_60/target_multisource_mcts.csv", index=False)