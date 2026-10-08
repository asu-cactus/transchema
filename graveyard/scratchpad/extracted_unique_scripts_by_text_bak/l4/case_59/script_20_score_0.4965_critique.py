import pandas as pd

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

def clean_int_column(col):
    return col.astype(str).str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False).str.replace(',', '', regex=False).astype(int)

df_all['Departamento'] = df_all['Departamento'].astype(str)
df_all['N.°'] = clean_int_column(df_all['N.°'])

# Convert Municipio strings to consistent integer codes
# Use factorize to assign unique integer codes to each Municipio string
df_all['Municipio'] = pd.factorize(df_all['Municipio'].astype(str))[0] + 1  # +1 to start codes at 1

df_all['Población cabecera'] = clean_int_column(df_all['Población cabecera'])
df_all['Población resto'] = clean_int_column(df_all['Población resto'])
df_all['Población Total'] = clean_int_column(df_all['Población Total'])

# Group by Departamento, N.°, Municipio and sum population columns
df_grouped = df_all.groupby(['Departamento', 'N.°', 'Municipio'], as_index=False).agg({
    'Población cabecera': 'sum',
    'Población resto': 'sum',
    'Población Total': 'sum'
})

# Reorder columns to match target schema exactly
df_grouped = df_grouped[['Departamento', 'N.°', 'Municipio', 'Población cabecera', 'Población resto', 'Población Total']]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_59/target_multisource_mcts.csv", index=False)