import pandas as pd

# Read all source tables with index_col=0 as instructed
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_20/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_20/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_20/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_20/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_20/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_20/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_20/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_20/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_20/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_20/training_9.csv", index_col=0)

# Join s3 (fact table) with each dimension table on descriptive columns to bring in IDs
r = pd.merge(s3, s0, how='left', left_on='Pronostico', right_on='Pronostico')
r = pd.merge(r, s1, how='left', left_on='Deteccion', right_on='Deteccion')
r = pd.merge(r, s2, how='left', left_on='Origen', right_on='Origen')
r = pd.merge(r, s4, how='left', left_on='Intervencion', right_on='Intervencion')
r = pd.merge(r, s5, how='left', left_on='Riesgo', right_on='Riesgo')
r = pd.merge(r, s6, how='left', left_on='Actividad', right_on='Actividad')
r = pd.merge(r, s7, how='left', left_on='Reanimacion', right_on='Reanimacion')
r = pd.merge(r, s8, how='left', left_on='Causa', right_on='Causa')
r = pd.merge(r, s9, how='left', left_on='Factor', right_on='Factor')

# Select columns in the exact order as target schema
cols = ['Fecha', 'Mes', 'IdAhogado', 'IdPersona', 'Localidad', 'Provincia', 'CCAA', 'Hora', 'Latitud_inc', 'Longitud_inc',
        'Sexo', 'Edad', 'Nacionalidad', 'Origen', 'Extraccion', 'Causa', 'TipoAhogamiento', 'Factor', 'Intervencion',
        'Pronostico', 'Localizacion', 'Riesgo', 'Reanimacion', 'Vigilancia', 'Actividad', 'Deteccion', 'ID', 'Estacion',
        'Estado', 'Latitud_est', 'Longitud_est', 'T_med', 'T_max', 'T_min', 'Precipitaciones', 'Presion', 'Dir. vi.',
        'V_Viento', 'Nubosidad', 'ProfNievecm', 'InsolacHoras', 'Distancia', 'IdActividad', 'IdCausa', 'IdDeteccion',
        'IdFactor', 'IdInterv', 'IdOrigen', 'IdPronostico', 'Mortal', 'IdReanima', 'IdRiesgo']

# Output the final result
result = r[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_20/target_multisource_mcts.csv", index=False)