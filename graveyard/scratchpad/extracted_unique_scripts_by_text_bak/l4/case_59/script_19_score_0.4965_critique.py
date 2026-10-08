import pandas as pd

def clean_int_column(s):
    return s.str.replace(r'\s', '', regex=True).str.replace(r'[^0-9]', '', regex=True).replace('', '0').astype(int)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_59/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

df_all['Población cabecera'] = clean_int_column(df_all['Población cabecera'])
df_all['Población resto'] = clean_int_column(df_all['Población resto'])
df_all['Población Total'] = clean_int_column(df_all['Población Total'])
df_all['N.°'] = df_all['N.°'].astype(int)

# Set 'Municipio' column to integer same as 'N.°' to match target schema
df_all['Municipio'] = df_all['N.°']

grouped = df_all.groupby(['Departamento', 'N.°'], as_index=False).agg({
    'Municipio': 'first',  # all same as N.°, so take first
    'Población cabecera': 'sum',
    'Población resto': 'sum',
    'Población Total': 'sum'
})

# Ensure 'Municipio' is integer type
grouped['Municipio'] = grouped['Municipio'].astype(int)

# Reorder columns to match target schema
grouped = grouped[['Departamento', 'N.°', 'Municipio', 'Población cabecera', 'Población resto', 'Población Total']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_59/target_multisource_mcts.csv", index=False)