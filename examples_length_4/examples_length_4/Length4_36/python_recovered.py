import pandas as pd

# Define file paths
path_source0 = 'autopipeline-benchmarks/github-pipelines/length4_36/test_0.csv'  # IdCausa, Causa
path_source1 = 'autopipeline-benchmarks/github-pipelines/length4_36/test_1.csv'  # IdDeteccion, Deteccion
path_source2 = 'autopipeline-benchmarks/github-pipelines/length4_36/test_2.csv'  # main detailed data, includes strings for Causa, Deteccion, etc.
path_source3 = 'autopipeline-benchmarks/github-pipelines/length4_36/test_3.csv'  # IdActividad, Actividad
path_source4 = 'autopipeline-benchmarks/github-pipelines/length4_36/test_4.csv'  # IdFactor, Factor

# Load all source tables with numerical index column as index_col=0
df_causa = pd.read_csv(path_source0, index_col=0)
df_deteccion = pd.read_csv(path_source1, index_col=0)
df_main = pd.read_csv(path_source2, index_col=0)
df_actividad = pd.read_csv(path_source3, index_col=0)
df_factor = pd.read_csv(path_source4, index_col=0)

# Join each Id mapping table to the main table on the string column

# Join df_causa on 'Causa'
df = df_main.merge(df_causa, on='Causa', how='left')  
# Rename IdCausa from df_causa to match target
df.rename(columns={'IdCausa': 'IdCausa'}, inplace=True)  # same name, just for clarity

# Join df_deteccion on 'Deteccion'
df = df.merge(df_deteccion, on='Deteccion', how='left')
df.rename(columns={'IdDeteccion': 'IdDeteccion'}, inplace=True)

# Join df_factor on 'Factor'
df = df.merge(df_factor, on='Factor', how='left')
df.rename(columns={'IdFactor': 'IdFactor'}, inplace=True)

# Join df_actividad on 'Actividad'
df = df.merge(df_actividad, on='Actividad', how='left')
df.rename(columns={'IdActividad': 'IdActividad'}, inplace=True)

# Now fix columns: target has both string and Id columns for Causa, Deteccion, Factor, Actividad

# In the target schema, the string columns exist (e.g. 'Causa', 'Deteccion', 'Factor', 'Actividad'),
# AND the corresponding Id columns exist:
# 'IdCausa', 'IdDeteccion', 'IdFactor', 'IdActividad'

# df now has all columns, including Causa (string), Deteccion (string), Factor (string), Actividad (string) 
# as well as IdCausa, IdDeteccion, IdFactor, IdActividad

# Drop 'Precipitaciones' column from main dataframe as it is NOT in target schema
if 'Precipitaciones' in df.columns:
    df.drop(columns=['Precipitaciones'], inplace=True)

# The target columns and types order must match the target schema exactly.

target_columns = ['Fecha', 'IdAhogado', 'IdPersona', 'Localidad', 'Provincia', 'CCAA', 'Hora', 
                  'Latitud_inc', 'Longitud_inc', 'Sexo', 'Edad', 'Nacionalidad', 'Origen', 'Extraccion', 
                  'Causa', 'TipoAhogamiento', 'Factor', 'Intervencion', 'Pronostico', 'Localizacion', 'Riesgo', 
                  'Reanimacion', 'Vigilancia', 'Actividad', 'Deteccion', 'ID', 'Estacion', 'Estado', 
                  'Latitud_est', 'Longitud_est', 'T_med', 'T_max', 'T_min', 'Presion', 'Dir. vi.', 'V_Viento', 
                  'Nubosidad', 'ProfNievecm', 'InsolacHoras', 'Distancia', 'IdActividad', 'IdCausa', 'IdDeteccion', 'IdFactor']

# Rename columns to be sure Ids are named properly (already done normally)
# The main source columns 'ID' is uppercase in target (not 'Id') so check case
# Confirm 'ID' column in df is 'ID' uppercase
if 'ID' not in df.columns and 'Id' in df.columns:
    df.rename(columns={'Id': 'ID'}, inplace=True)

# Defensive filtering to ensure all needed columns exist, fill missing with NaN if necessary
for col in target_columns:
    if col not in df.columns:
        df[col] = pd.NA

# Reorder columns to target_columns
df_target = df[target_columns].copy()

# Fix data types according to target schema
# According to target schema info in prompt:

# ['Fecha': string, 'IdAhogado': integer, 'IdPersona': integer, ...]
# We'll convert for safer typing:

dtype_conversion = {
    'Fecha': str,
    'IdAhogado': 'Int64',  # use pandas nullable integer dtype
    'IdPersona': 'Int64',
    'Localidad': str,
    'Provincia': str,
    'CCAA': str,
    'Hora': str,
    'Latitud_inc': float,
    'Longitud_inc': float,
    'Sexo': str,
    'Edad': float,
    'Nacionalidad': str,
    'Origen': str,
    'Extraccion': str,
    'Causa': str,
    'TipoAhogamiento': str,
    'Factor': str,
    'Intervencion': str,
    'Pronostico': str,
    'Localizacion': str,
    'Riesgo': str,
    'Reanimacion': str,
    'Vigilancia': str,
    'Actividad': str,
    'Deteccion': str,
    'ID': 'Int64',
    'Estacion': str,
    'Estado': str,
    'Latitud_est': float,
    'Longitud_est': float,
    'T_med': float,
    'T_max': float,
    'T_min': float,
    'Presion': float,
    'Dir. vi.': float,
    'V_Viento': 'Int64',
    'Nubosidad': float,
    'ProfNievecm': float,
    'InsolacHoras': float,
    'Distancia': float,
    'IdActividad': 'Int64',
    'IdCausa': 'Int64',
    'IdDeteccion': 'Int64',
    'IdFactor': 'Int64',
}

for col, dt in dtype_conversion.items():
    if col in df_target.columns:
        try:
            if dt == str:
                df_target[col] = df_target[col].astype(str).replace({'nan':'', 'NaN': '', 'None': ''})
            else:
                df_target[col] = pd.to_numeric(df_target[col], errors='coerce').astype(dt)
        except Exception:
            # If conversion fails, keep as is (best effort)
            pass

# According to example, 'Hora' format in target is like '6:00', '19:20' (string), preserve as is.

# Save to CSV with no index
df_target.to_csv('autopipeline-benchmarks/github-pipelines/length4_36/target_multisource_cot.csv', index=False)