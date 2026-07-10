import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_37/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_37/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_37/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_37/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_37/training_4.csv", index_col=0)

df = pd.merge(source2, source0, on="IdInterv", how="left", suffixes=('', '_src0'))
df = pd.merge(df, source1, on="IdDeteccion", how="left", suffixes=('', '_src1'))
df = pd.merge(df, source3, on="IdActividad", how="left", suffixes=('', '_src3'))
df = pd.merge(df, source4, on="IdCausa", how="left", suffixes=('', '_src4'))

df = df.rename(columns={
    'Intervencion_src0': 'Intervencion',
    'Deteccion_src1': 'Deteccion',
    'Actividad': 'Actividad',
    'Causa_src4': 'Causa'
})

# Drop duplicate columns from source tables after join if any
drop_cols = [col for col in df.columns if col.endswith('_src0') or col.endswith('_src1') or col.endswith('_src3') or col.endswith('_src4')]
df = df.drop(columns=drop_cols)

# Select and reorder columns to match target schema exactly
target_columns = ['Fecha', 'IdAhogado', 'IdPersona', 'Localidad', 'Provincia', 'CCAA', 'Hora', 'Latitud_inc', 'Longitud_inc', 'Sexo', 'Edad', 'Nacionalidad', 'Origen', 'Extraccion', 'Causa', 'TipoAhogamiento', 'Factor', 'Intervencion', 'Pronostico', 'Localizacion', 'Riesgo', 'Reanimacion', 'Vigilancia', 'Actividad', 'Deteccion', 'ID', 'Estacion', 'Estado', 'Latitud_est', 'Longitud_est', 'T_med', 'T_max', 'T_min', 'Presion', 'Dir. vi.', 'V_Viento', 'Nubosidad', 'ProfNievecm', 'InsolacHoras', 'Distancia', 'IdActividad', 'IdCausa', 'IdDeteccion', 'IdInterv']

df = df[target_columns]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_37/target_multisource_mcts.csv", index=False)