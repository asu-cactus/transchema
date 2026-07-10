import pandas as pd

# Read all source CSVs
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_4.csv", index_col=0)

# Concatenate all sources
df = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

# Convert 'precio' to numeric, coercing errors to NaN
df['precio'] = pd.to_numeric(df['precio'], errors='coerce')

# Group by 'titulo' and 'tipo' (leftmost string columns, likely unique keys)
# Aggregate 'precio' by mean, other columns by first non-null value
agg_dict = {
    'precio': 'mean',
    'condicion': 'first',
    'ubicacion': 'first',
    'tiempo': 'first',
    'reputacion': 'first',
    'pago': 'first'
}

df_grouped = df.groupby(['titulo', 'tipo'], dropna=False, as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
df_grouped = df_grouped[['titulo', 'tipo', 'precio', 'condicion', 'ubicacion', 'tiempo', 'reputacion', 'pago']]

# Write to target CSV
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_86/target_multisource_mcts.csv", index=False)