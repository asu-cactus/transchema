import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_4.csv", index_col=0)

join_01 = pd.merge(df0, df1, on="titulo", suffixes=('_0', '_1'))
join_012 = pd.merge(join_01, df2, on="titulo")
join_012 = join_012.rename(columns={col: col+'_2' for col in df2.columns if col != 'titulo'})
join_0123 = pd.merge(join_012, df3, on="titulo")
join_0123 = join_0123.rename(columns={col: col+'_3' for col in df3.columns if col != 'titulo'})
join_all = pd.merge(join_0123, df4, on="titulo")
join_all = join_all.rename(columns={col: col+'_4' for col in df4.columns if col != 'titulo'})

group_by_cols = [
    'titulo',
    'tipo_0',
    'condicion_1',
    'ubicacion_0',
    'tiempo_0',
    'reputacion_0',
    'pago_0'
]

agg_dict = {
    'precio_0': 'mean',
    'precio_1': 'mean',
    'precio_2': 'mean',
    'precio_3': 'mean',
    'precio_4': 'mean'
}

grouped = join_all.groupby(group_by_cols).agg(agg_dict).reset_index()

grouped['precio'] = grouped[['precio_0', 'precio_1', 'precio_2', 'precio_3', 'precio_4']].mean(axis=1)

result = grouped[['titulo', 'tipo_0', 'precio', 'condicion_1', 'ubicacion_0', 'tiempo_0', 'reputacion_0', 'pago_0']]

result.columns = ['titulo', 'tipo', 'precio', 'condicion', 'ubicacion', 'tiempo', 'reputacion', 'pago']

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_86/target_multisource_mcts.csv", index=False)