import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_21/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_21/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_21/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_21/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_21/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_21/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_21/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_21/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_21/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_21/training_9.csv", index_col=0)
s10 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_21/training_10.csv", index_col=0)

df = s5.merge(s0, how='left', left_on='Origen', right_on='Origen', suffixes=('', '_s0'))
df = df.merge(s1, how='left', left_on='Pronostico', right_on='Pronostico', suffixes=('', '_s1'))
df = df.merge(s2, how='left', left_on='Deteccion', right_on='Deteccion', suffixes=('', '_s2'))
df = df.merge(s3, how='left', left_on='TipoAhogamiento', right_on='TipoAhogamiento', suffixes=('', '_s3'))
df = df.merge(s4, how='left', left_on='Intervencion', right_on='Intervencion', suffixes=('', '_s4'))
df = df.merge(s6, how='left', left_on='Actividad', right_on='Actividad', suffixes=('', '_s6'))
df = df.merge(s7, how='left', left_on='Causa', right_on='Causa', suffixes=('', '_s7'))
df = df.merge(s8, how='left', left_on='Reanimacion', right_on='Reanimacion', suffixes=('', '_s8'))
df = df.merge(s9, how='left', left_on='Riesgo', right_on='Riesgo', suffixes=('', '_s9'))
df = df.merge(s10, how='left', left_on='Factor', right_on='Factor', suffixes=('', '_s10'))

# Select and reorder columns to match target schema
target_cols = ['Fecha', 'Mes', 'IdAhogado', 'IdPersona', 'Localidad', 'Provincia', 'CCAA', 'Hora',
               'Latitud_inc', 'Longitud_inc', 'Sexo', 'Edad', 'Nacionalidad', 'Origen', 'Extraccion',
               'Causa', 'TipoAhogamiento', 'Factor', 'Intervencion', 'Pronostico', 'Localizacion',
               'Riesgo', 'Reanimacion', 'Vigilancia', 'Actividad', 'Deteccion', 'ID', 'Estacion',
               'Estado', 'Latitud_est', 'Longitud_est', 'T_med', 'T_max', 'T_min', 'Precipitaciones',
               'Presion', 'Dir. vi.', 'V_Viento', 'Nubosidad', 'ProfNievecm', 'InsolacHoras', 'Distancia',
               'IdActividad', 'IdCausa', 'IdDeteccion', 'IdFactor', 'IdInterv', 'IdOrigen', 'IdPronostico',
               'Mortal', 'IdReanima', 'IdRiesgo', 'IdTipo']

df_final = df[target_cols]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length9_21/target_multisource_mcts.csv", index=False)