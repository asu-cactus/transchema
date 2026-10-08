import pandas as pd

def clean_population_column(col):
    return col.astype(str).str.replace(r'\s', '', regex=True).str.replace(' ', '', regex=False).str.replace(',', '').astype(int)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_59/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    df['Población cabecera'] = clean_population_column(df['Población cabecera'])
    df['Población resto'] = clean_population_column(df['Población resto'])
    df['Población Total'] = clean_population_column(df['Población Total'])
    df['N.°'] = pd.to_numeric(df['N.°'], errors='coerce').astype('Int64')
    # Keep Municipio as string (do not convert to numeric)
    df['Municipio'] = df['Municipio'].astype(str)
    df['Departamento'] = df['Departamento'].astype(str)
    dfs.append(df)

union_df = pd.concat(dfs, ignore_index=True)

agg_df = union_df.groupby(['Departamento', 'N.°'], dropna=False).agg({
    'Población cabecera': 'sum',
    'Población resto': 'sum',
    'Población Total': 'sum'
}).reset_index()

# Assign Municipio = N.° to match target schema
agg_df['Municipio'] = agg_df['N.°']

# Reorder columns to match target schema
agg_df = agg_df[['Departamento', 'N.°', 'Municipio', 'Población cabecera', 'Población resto', 'Población Total']]

# Convert population columns to int (already int from sum)
agg_df['Población cabecera'] = agg_df['Población cabecera'].astype('Int64')
agg_df['Población resto'] = agg_df['Población resto'].astype('Int64')
agg_df['Población Total'] = agg_df['Población Total'].astype('Int64')

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_59/target_multisource_mcts.csv", index=False)