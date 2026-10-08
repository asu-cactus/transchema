import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_4.csv", index_col=0)

all_sources = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

target_cols = ['titulo', 'tipo', 'precio', 'condicion', 'ubicacion', 'tiempo', 'reputacion', 'pago']
all_sources = all_sources[target_cols]

all_sources['titulo'] = all_sources['titulo'].astype(str)
all_sources['tipo'] = all_sources['tipo'].astype(str)
all_sources['precio'] = pd.to_numeric(all_sources['precio'], errors='coerce')
all_sources['condicion'] = all_sources['condicion'].astype(str)
all_sources['ubicacion'] = all_sources['ubicacion'].astype(str)
all_sources['tiempo'] = all_sources['tiempo'].astype(str)
# Keep reputacion as is to preserve NaNs, do not convert to string forcibly
# all_sources['reputacion'] = all_sources['reputacion'].astype(str)
all_sources['pago'] = all_sources['pago'].astype(str)

all_sources.to_csv("autopipeline-benchmarks/github-pipelines/length4_86/target_multisource_mcts.csv", index=False)