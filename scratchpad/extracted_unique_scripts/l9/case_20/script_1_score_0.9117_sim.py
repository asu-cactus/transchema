import pandas as pd

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

r1 = pd.merge(s3, s0, how='left', left_on='Pronostico', right_on='Pronostico')
r2 = pd.merge(r1, s1, how='left', left_on='Deteccion', right_on='Deteccion')
r3 = pd.merge(r2, s2, how='left', left_on='Origen', right_on='Origen')
r4 = pd.merge(r3, s4, how='left', left_on='Intervencion', right_on='Intervencion')
r5 = pd.merge(r4, s5, how='left', left_on='Riesgo', right_on='Riesgo')
r6 = pd.merge(r5, s6, how='left', left_on='Actividad', right_on='Actividad')
r7 = pd.merge(r6, s7, how='left', left_on='Reanimacion', right_on='Reanimacion')
r8 = pd.merge(r7, s8, how='left', left_on='Causa', right_on='Causa')
r9 = pd.merge(r8, s9, how='left', left_on='Factor', right_on='Factor')

cols = ['Fecha', 'Mes', 'IdAhogado', 'IdPersona', 'Localidad', 'Provincia', 'CCAA', 'Hora', 'Latitud_inc', 'Longitud_inc',
        'Sexo', 'Edad', 'Nacionalidad', 'Origen', 'Extraccion', 'Causa', 'TipoAhogamiento', 'Factor', 'Intervencion',
        'Pronostico', 'Localizacion', 'Riesgo', 'Reanimacion', 'Vigilancia', 'Actividad', 'Deteccion', 'ID', 'Estacion',
        'Estado', 'Latitud_est', 'Longitud_est', 'T_med', 'T_max', 'T_min', 'Precipitaciones', 'Presion', 'Dir. vi.',
        'V_Viento', 'Nubosidad', 'ProfNievecm', 'InsolacHoras', 'Distancia', 'IdActividad', 'IdCausa', 'IdDeteccion',
        'IdFactor', 'IdInterv', 'IdOrigen', 'IdPronostico', 'Mortal', 'IdReanima', 'IdRiesgo']

result = r9[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_20/target_multisource_mcts.csv", index=False)