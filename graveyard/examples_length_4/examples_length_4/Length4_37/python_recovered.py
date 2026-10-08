import pandas as pd
import numpy as np

# File paths for sources
path_0 = 'autopipeline-benchmarks/github-pipelines/length4_37/test_0.csv'  # Source4_37_0: IdInterv, Intervencion
path_1 = 'autopipeline-benchmarks/github-pipelines/length4_37/test_1.csv'  # Source4_37_1: IdDeteccion, Deteccion
path_2 = 'autopipeline-benchmarks/github-pipelines/length4_37/test_2.csv'  # Source4_37_2: main detailed records
path_3 = 'autopipeline-benchmarks/github-pipelines/length4_37/test_3.csv'  # Source4_37_3: IdActividad, Actividad
path_4 = 'autopipeline-benchmarks/github-pipelines/length4_37/test_4.csv'  # Source4_37_4: IdCausa, Causa

# Load the source data
df_0 = pd.read_csv(path_0, index_col=0)  # IdInterv, Intervencion
df_1 = pd.read_csv(path_1, index_col=0)  # IdDeteccion, Deteccion
df_2 = pd.read_csv(path_2, index_col=0)  # Main detailed data
df_3 = pd.read_csv(path_3, index_col=0)  # IdActividad, Actividad
df_4 = pd.read_csv(path_4, index_col=0)  # IdCausa, Causa

# -- Step 1: Replace coded columns in df_2 with descriptive columns via JOIN --

# Join df_2 with df_0 on Intervencion (string) to get IdInterv
# But df_2 has "Intervencion" string and df_0 has "IdInterv" and "Intervencion" string.
# We want to replace df_2.Intervencion (string) by id (idInterv) -> So join on 'Intervencion'
df_2 = df_2.merge(df_0[['IdInterv','Intervencion']], how='left', on='Intervencion')

# Join df_2 with df_1 on Deteccion string to get IdDeteccion
df_2 = df_2.merge(df_1[['IdDeteccion', 'Deteccion']], how='left', on='Deteccion')

# Join df_2 with df_3 on Actividad string to get IdActividad
df_2 = df_2.merge(df_3[['IdActividad', 'Actividad']], how='left', on='Actividad')

# Join df_2 with df_4 on Causa string to get IdCausa
df_2 = df_2.merge(df_4[['IdCausa', 'Causa']], how='left', on='Causa')

# Rename / reorder columns and handle columns not in df_2 yet.

# df_2 columns (after merges):
# original columns + IdInterv, IdDeteccion, IdActividad, IdCausa

# The target schema columns are:
# ['Fecha': string, 'IdAhogado': int, 'IdPersona': int, 'Localidad': string, 'Provincia': string, 'CCAA': string, 
# 'Hora': string, 'Latitud_inc': float, 'Longitud_inc': float, 'Sexo': string, 'Edad': float, 'Nacionalidad': string, 
# 'Origen': string, 'Extraccion': string, 'Causa': string, 'TipoAhogamiento': string, 'Factor': string, 'Intervencion': string, 
# 'Pronostico': string, 'Localizacion': string, 'Riesgo': string, 'Reanimacion': string, 'Vigilancia': string, 'Actividad': string, 
# 'Deteccion': string, 'ID': int, 'Estacion': string, 'Estado': string, 'Latitud_est': float, 'Longitud_est': float, 'T_med': float, 
# 'T_max': float, 'T_min': float, 'Presion': float, 'Dir. vi.': float, 'V_Viento': int, 'Nubosidad': float, 'ProfNievecm': float, 
# 'InsolacHoras': float, 'Distancia': float, 'IdActividad': int, 'IdCausa': int, 'IdDeteccion': int, 'IdInterv': int]

# Check if column "Precipitaciones" is in df_2 but not in target: must be dropped
if 'Precipitaciones' in df_2.columns:
    df_2 = df_2.drop(columns=['Precipitaciones'])

# Handle data types conversions to match target schema

# Fecha - ensure string format as in target (looks like dd/mm/yyyy)
# It likely is string, so keep as is
df_2['Fecha'] = df_2['Fecha'].astype(str)

# IdAhogado, IdPersona, ID - ensure integer
df_2['IdAhogado'] = df_2['IdAhogado'].astype(int)
df_2['IdPersona'] = df_2['IdPersona'].astype(int)
df_2['ID'] = df_2['ID'].astype(int)

# Ensure Latitud_inc, Longitud_inc as float
df_2['Latitud_inc'] = df_2['Latitud_inc'].astype(float)
df_2['Longitud_inc'] = df_2['Longitud_inc'].astype(float)

# Sexo string - ensure string
df_2['Sexo'] = df_2['Sexo'].astype(str)

# Edad float (from examples)
df_2['Edad'] = pd.to_numeric(df_2['Edad'], errors='coerce').astype(float)

# Nacionalidad, Origen, Extraccion - string
df_2['Nacionalidad'] = df_2['Nacionalidad'].astype(str)
df_2['Origen'] = df_2['Origen'].astype(str)
df_2['Extraccion'] = df_2['Extraccion'].astype(str)

# Causa, TipoAhogamiento, Factor, Intervencion, Pronostico, Localizacion, Riesgo, Reanimacion, Vigilancia,
# Actividad, Deteccion - all string
str_cols = ['Causa', 'TipoAhogamiento', 'Factor', 'Intervencion', 'Pronostico', 'Localizacion', 'Riesgo',
            'Reanimacion', 'Vigilancia', 'Actividad', 'Deteccion']
for col in str_cols:
    df_2[col] = df_2[col].astype(str)

# Estacion, Estado - string
df_2['Estacion'] = df_2['Estacion'].astype(str)
df_2['Estado'] = df_2['Estado'].astype(str)

# Latitud_est, Longitud_est - float
df_2['Latitud_est'] = df_2['Latitud_est'].astype(float)
df_2['Longitud_est'] = df_2['Longitud_est'].astype(float)

# T_med, T_max, T_min, Presion, Dir. vi., Nubosidad, ProfNievecm, InsolacHoras, Distancia - float,
# V_Viento - int
df_2['T_med'] = df_2['T_med'].astype(float)
df_2['T_max'] = df_2['T_max'].astype(float)
df_2['T_min'] = df_2['T_min'].astype(float)
df_2['Presion'] = df_2['Presion'].astype(float)
df_2['Dir. vi.'] = df_2['Dir. vi.'].astype(float)
df_2['V_Viento'] = df_2['V_Viento'].astype(int)
df_2['Nubosidad'] = df_2['Nubosidad'].astype(float)
df_2['ProfNievecm'] = df_2['ProfNievecm'].astype(float)
df_2['InsolacHoras'] = df_2['InsolacHoras'].astype(float)
df_2['Distancia'] = df_2['Distancia'].astype(float)

# IdActividad, IdCausa, IdDeteccion, IdInterv - int
df_2['IdActividad'] = df_2['IdActividad'].fillna(0).astype(int)
df_2['IdCausa'] = df_2['IdCausa'].fillna(0).astype(int)
df_2['IdDeteccion'] = df_2['IdDeteccion'].fillna(0).astype(int)
df_2['IdInterv'] = df_2['IdInterv'].fillna(0).astype(int)

# Select and reorder columns to match target schema exactly
target_columns = ['Fecha', 'IdAhogado', 'IdPersona', 'Localidad', 'Provincia', 'CCAA', 'Hora',
                  'Latitud_inc', 'Longitud_inc', 'Sexo', 'Edad', 'Nacionalidad', 'Origen', 'Extraccion',
                  'Causa', 'TipoAhogamiento', 'Factor', 'Intervencion', 'Pronostico', 'Localizacion', 'Riesgo',
                  'Reanimacion', 'Vigilancia', 'Actividad', 'Deteccion', 'ID', 'Estacion', 'Estado',
                  'Latitud_est', 'Longitud_est', 'T_med', 'T_max', 'T_min', 'Presion', 'Dir. vi.', 'V_Viento',
                  'Nubosidad', 'ProfNievecm', 'InsolacHoras', 'Distancia', 'IdActividad', 'IdCausa',
                  'IdDeteccion', 'IdInterv']

df_target = df_2[target_columns]

# Export to CSV without index as specified
df_target.to_csv('autopipeline-benchmarks/github-pipelines/length4_37/target_multisource_cot.csv', index=False)