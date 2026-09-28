import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_4.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

# Ensure precio is float type as in target schema
df_all['precio'] = df_all['precio'].astype(float)

# Reorder columns exactly as target schema
df_all = df_all[['titulo', 'tipo', 'precio', 'condicion', 'ubicacion', 'tiempo', 'reputacion', 'pago']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_86/target_multisource_mcts.csv", index=False)