import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_21/training_0.csv", index_col=0)   # IdOrigen, Origen
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_21/training_1.csv", index_col=0)   # IdPronostico, Pronostico, Mortal
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_21/training_2.csv", index_col=0)   # IdDeteccion, Deteccion
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_21/training_3.csv", index_col=0)   # IdTipo, TipoAhogamiento
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_21/training_4.csv", index_col=0)   # IdInterv, Intervencion
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_21/training_5.csv", index_col=0)   # main table
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_21/training_6.csv", index_col=0)   # IdActividad, Actividad
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_21/training_7.csv", index_col=0)   # IdCausa, Causa
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_21/training_8.csv", index_col=0)   # IdReanima, Reanimacion
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_21/training_9.csv", index_col=0)   # IdRiesgo, Riesgo
s10 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_21/training_10.csv", index_col=0) # IdFactor, Factor

# Join s5 with s0 on Origen to get IdOrigen
df = pd.merge(s5, s0, how='left', left_on='Origen', right_on='Origen')

# Join with s1 on Pronostico to get IdPronostico and Mortal
df = pd.merge(df, s1, how='left', left_on='Pronostico', right_on='Pronostico')

# Join with s2 on Deteccion to get IdDeteccion
df = pd.merge(df, s2, how='left', left_on='Deteccion', right_on='Deteccion')

# Join with s3 on TipoAhogamiento to get IdTipo
df = pd.merge(df, s3, how='left', left_on='TipoAhogamiento', right_on='TipoAhogamiento')

# Join with s4 on Intervencion to get IdInterv
df = pd.merge(df, s4, how='left', left_on='Intervencion', right_on='Intervencion')

# Join with s6 on Actividad to get IdActividad
df = pd.merge(df, s6, how='left', left_on='Actividad', right_on='Actividad')

# Join with s7 on Causa to get IdCausa
df = pd.merge(df, s7, how='left', left_on='Causa', right_on='Causa')

# Join with s8 on Reanimacion to get IdReanima
df = pd.merge(df, s8, how='left', left_on='Reanimacion', right_on='Reanimacion')

# Join with s9 on Riesgo to get IdRiesgo
df = pd.merge(df, s9, how='left', left_on='Riesgo', right_on='Riesgo')

# Join with s10 on Factor to get IdFactor
df = pd.merge(df, s10, how='left', left_on='Factor', right_on='Factor')

# Select and reorder columns exactly as in target schema
target_cols = ['Fecha', 'Mes', 'IdAhogado', 'IdPersona', 'Localidad', 'Provincia', 'CCAA', 'Hora',
               'Latitud_inc', 'Longitud_inc', 'Sexo', 'Edad', 'Nacionalidad', 'Origen', 'Extraccion',
               'Causa', 'TipoAhogamiento', 'Factor', 'Intervencion', 'Pronostico', 'Localizacion',
               'Riesgo', 'Reanimacion', 'Vigilancia', 'Actividad', 'Deteccion', 'ID', 'Estacion',
               'Estado', 'Latitud_est', 'Longitud_est', 'T_med', 'T_max', 'T_min', 'Precipitaciones',
               'Presion', 'Dir. vi.', 'V_Viento', 'Nubosidad', 'ProfNievecm', 'InsolacHoras', 'Distancia',
               'IdActividad', 'IdCausa', 'IdDeteccion', 'IdFactor', 'IdInterv', 'IdOrigen', 'IdPronostico',
               'Mortal', 'IdReanima', 'IdRiesgo', 'IdTipo']

df = df[target_cols]

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_21/target_multisource_mcts.csv", index=False)