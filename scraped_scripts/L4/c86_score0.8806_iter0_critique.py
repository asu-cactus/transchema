import pandas as pd

# Read all source CSV files with index_col=0 to ignore the numerical index column
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_4.csv", index_col=0)

# UNION all sources (concatenate)
df = pd.concat([source0, source1, source2, source3, source4], ignore_index=True)

# Define aggregation dictionary:
# - precio: mean
# - other string columns: first non-null value
agg_dict = {
    'precio': 'mean',
    'condicion': 'first',
    'ubicacion': 'first',
    'tiempo': 'first',
    'reputacion': 'first',
    'pago': 'first'
}

# GROUP BY titulo and tipo, aggregate accordingly
result = df.groupby(['titulo', 'tipo'], dropna=False, as_index=False).agg(agg_dict)

# Ensure columns order matches target schema exactly
result = result[['titulo', 'tipo', 'precio', 'condicion', 'ubicacion', 'tiempo', 'reputacion', 'pago']]

# Write to target CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_86/target_multisource_mcts.csv", index=False)