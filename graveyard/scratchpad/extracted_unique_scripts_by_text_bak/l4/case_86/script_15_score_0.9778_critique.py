import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_4.csv", index_col=0)

# Concatenate all source tables (all have the same schema)
df_final = pd.concat([df0, df1, df2, df3, df4], ignore_index=True, sort=False)

# Ensure correct dtypes matching target schema
df_final['titulo'] = df_final['titulo'].astype(str)
df_final['tipo'] = df_final['tipo'].astype(str)
df_final['precio'] = pd.to_numeric(df_final['precio'], errors='coerce')
df_final['condicion'] = df_final['condicion'].astype(str)
df_final['ubicacion'] = df_final['ubicacion'].astype(str)
df_final['tiempo'] = df_final['tiempo'].astype(str)
df_final['reputacion'] = df_final['reputacion'].astype(str)
df_final['pago'] = df_final['pago'].astype(str)

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_86/target_multisource_mcts.csv", index=False)