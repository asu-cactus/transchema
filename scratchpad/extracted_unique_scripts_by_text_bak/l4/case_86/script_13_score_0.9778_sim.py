import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_4.csv", index_col=0)

joined_0_1 = pd.merge(df0, df1, on='titulo', suffixes=('_0', '_1'))

# The join is only a partial step, but the target schema matches source schemas exactly.
# So we union all source tables (including df0 and df1) to get the final target table.
# The join result is not used further because union of all sources is the final step.

all_sources = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

# Ensure columns are in target schema order and types
target_cols = ['titulo', 'tipo', 'precio', 'condicion', 'ubicacion', 'tiempo', 'reputacion', 'pago']
all_sources = all_sources[target_cols]

all_sources['titulo'] = all_sources['titulo'].astype(str)
all_sources['tipo'] = all_sources['tipo'].astype(str)
all_sources['precio'] = pd.to_numeric(all_sources['precio'], errors='coerce')
all_sources['condicion'] = all_sources['condicion'].astype(str)
all_sources['ubicacion'] = all_sources['ubicacion'].astype(str)
all_sources['tiempo'] = all_sources['tiempo'].astype(str)
all_sources['reputacion'] = all_sources['reputacion'].astype(str)
all_sources['pago'] = all_sources['pago'].astype(str)

all_sources.to_csv("autopipeline-benchmarks/github-pipelines/length4_86/target_multisource_mcts.csv", index=False)