import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_36/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_36/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_36/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_36/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_36/training_4.csv", index_col=0)

df = s2.merge(s0, how='left', on='IdCausa', suffixes=('', '_s0'))
df = df.drop(columns=['Causa'])  # drop original Causa from s2 to avoid confusion
df = df.rename(columns={'Causa_s0': 'Causa'})

df = df.merge(s1, how='left', on='Deteccion', suffixes=('', '_s1'))
df = df.drop(columns=['Deteccion'])  # drop original Deteccion from s2
df = df.rename(columns={'Deteccion_s1': 'Deteccion'})

df = df.merge(s3, how='left', on='Actividad', suffixes=('', '_s3'))
df = df.drop(columns=['Actividad'])
df = df.rename(columns={'Actividad_s3': 'Actividad'})

df = df.merge(s4, how='left', on='Factor', suffixes=('', '_s4'))
df = df.drop(columns=['Factor'])
df = df.rename(columns={'Factor_s4': 'Factor'})

# Reorder columns to match target schema exactly
target_cols = ['Fecha', 'IdAhogado', 'IdPersona', 'Localidad', 'Provincia', 'CCAA', 'Hora',
               'Latitud_inc', 'Longitud_inc', 'Sexo', 'Edad', 'Nacionalidad', 'Origen', 'Extraccion',
               'Causa', 'TipoAhogamiento', 'Factor', 'Intervencion', 'Pronostico', 'Localizacion',
               'Riesgo', 'Reanimacion', 'Vigilancia', 'Actividad', 'Deteccion', 'ID', 'Estacion',
               'Estado', 'Latitud_est', 'Longitud_est', 'T_med', 'T_max', 'T_min', 'Presion',
               'Dir. vi.', 'V_Viento', 'Nubosidad', 'ProfNievecm', 'InsolacHoras', 'Distancia',
               'IdActividad', 'IdCausa', 'IdDeteccion', 'IdFactor']

# Ensure all target columns exist in df, if not create with NaN
for c in target_cols:
    if c not in df.columns:
        df[c] = pd.NA

df = df[target_cols]

# Fix data types according to target schema
df['Fecha'] = df['Fecha'].astype(str)
df['IdAhogado'] = pd.to_numeric(df['IdAhogado'], errors='coerce').astype('Int64')
df['IdPersona'] = pd.to_numeric(df['IdPersona'], errors='coerce').astype('Int64')
df['Localidad'] = df['Localidad'].astype(str)
df['Provincia'] = df['Provincia'].astype(str)
df['CCAA'] = df['CCAA'].astype(str)
df['Hora'] = df['Hora'].astype(str)
df['Latitud_inc'] = pd.to_numeric(df['Latitud_inc'], errors='coerce').astype(float)
df['Longitud_inc'] = pd.to_numeric(df['Longitud_inc'], errors='coerce').astype(float)
df['Sexo'] = df['Sexo'].astype(str)
df['Edad'] = pd.to_numeric(df['Edad'], errors='coerce').astype(float)
df['Nacionalidad'] = df['Nacionalidad'].astype(str)
df['Origen'] = df['Origen'].astype(str)
df['Extraccion'] = df['Extraccion'].astype(str)
df['Causa'] = df['Causa'].astype(str)
df['TipoAhogamiento'] = df['TipoAhogamiento'].astype(str)
df['Factor'] = df['Factor'].astype(str)
df['Intervencion'] = df['Intervencion'].astype(str)
df['Pronostico'] = df['Pronostico'].astype(str)
df['Localizacion'] = df['Localizacion'].astype(str)
df['Riesgo'] = df['Riesgo'].astype(str)
df['Reanimacion'] = df['Reanimacion'].astype(str)
df['Vigilancia'] = df['Vigilancia'].astype(str)
df['Actividad'] = df['Actividad'].astype(str)
df['Deteccion'] = df['Deteccion'].astype(str)
df['ID'] = pd.to_numeric(df['ID'], errors='coerce').astype('Int64')
df['Estacion'] = df['Estacion'].astype(str)
df['Estado'] = df['Estado'].astype(str)
df['Latitud_est'] = pd.to_numeric(df['Latitud_est'], errors='coerce').astype(float)
df['Longitud_est'] = pd.to_numeric(df['Longitud_est'], errors='coerce').astype(float)
df['T_med'] = pd.to_numeric(df['T_med'], errors='coerce').astype(float)
df['T_max'] = pd.to_numeric(df['T_max'], errors='coerce').astype(float)
df['T_min'] = pd.to_numeric(df['T_min'], errors='coerce').astype(float)
df['Presion'] = pd.to_numeric(df['Presion'], errors='coerce').astype(float)
df['Dir. vi.'] = pd.to_numeric(df['Dir. vi.'], errors='coerce').astype(float)
df['V_Viento'] = pd.to_numeric(df['V_Viento'], errors='coerce').astype('Int64')
df['Nubosidad'] = pd.to_numeric(df['Nubosidad'], errors='coerce').astype(float)
df['ProfNievecm'] = pd.to_numeric(df['ProfNievecm'], errors='coerce').astype(float)
df['InsolacHoras'] = pd.to_numeric(df['InsolacHoras'], errors='coerce').astype(float)
df['Distancia'] = pd.to_numeric(df['Distancia'], errors='coerce').astype(float)
df['IdActividad'] = pd.to_numeric(df['IdActividad'], errors='coerce').astype('Int64')
df['IdCausa'] = pd.to_numeric(df['IdCausa'], errors='coerce').astype('Int64')
df['IdDeteccion'] = pd.to_numeric(df['IdDeteccion'], errors='coerce').astype('Int64')
df['IdFactor'] = pd.to_numeric(df['IdFactor'], errors='coerce').astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_36/target_multisource_mcts.csv", index=False)