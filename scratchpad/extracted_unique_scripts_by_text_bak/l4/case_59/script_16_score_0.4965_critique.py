import pandas as pd

def clean_number_column(col):
    return col.str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False).astype(int)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_59/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    df['Población cabecera'] = clean_number_column(df['Población cabecera'])
    df['Población resto'] = clean_number_column(df['Población resto'])
    df['Población Total'] = clean_number_column(df['Población Total'])
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

# Create 'Municipio' column as integer copy of 'N.°' to match target schema
df_all['Municipio'] = df_all['N.°']

agg = df_all.groupby(['Departamento', 'N.°', 'Municipio'], as_index=False).agg({
    'Población cabecera': 'sum',
    'Población resto': 'sum',
    'Población Total': 'sum'
})

# Reorder columns to match target schema
agg = agg[['Departamento', 'N.°', 'Municipio', 'Población cabecera', 'Población resto', 'Población Total']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_59/target_multisource_mcts.csv", index=False)