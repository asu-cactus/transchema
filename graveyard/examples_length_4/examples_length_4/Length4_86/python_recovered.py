import pandas as pd

# File paths for all source CSV files (given in the prompt)
source_files = [
    'autopipeline-benchmarks/github-pipelines/length4_86/test_0.csv',
    'autopipeline-benchmarks/github-pipelines/length4_86/test_1.csv',
    'autopipeline-benchmarks/github-pipelines/length4_86/test_2.csv',
    'autopipeline-benchmarks/github-pipelines/length4_86/test_3.csv',
    'autopipeline-benchmarks/github-pipelines/length4_86/test_4.csv'
]

# Load all source tables into a list of dataframes, skip the numerical index column (index_col=0)
dfs = [pd.read_csv(f, index_col=0) for f in source_files]

# All source tables have exactly the same schema as the target.
# The target schema is:
# ['titulo', 'tipo', 'precio', 'condicion', 'ubicacion', 'tiempo', 'reputacion', 'pago']

# According to instructions and hints:
# Since all sources share the exact schema as the target and must be all used,
# UNION (concatenation) of all sources is the correct operation.

# Concatenate all dataframes (union) vertically (ignore index for clean concatenation)
df_all = pd.concat(dfs, ignore_index=True)

# Data type corrections and transformations to match target schema and examples:

# 1. 'precio' column should be float
# Source data 'precio' might have comma separators "599.000" which should be interpreted as numbers, 
# but looking at the examples, prices use dot as thousand separator? 
# Actually, in examples like '599.000' the dot probably means thousands separator,
# so we need to parse precio as float, replacing dots that separate thousands and commas decimal points if any.

# The 'precio' values appear as strings with dots for thousand separator,
# to convert to float, replace '.' with '', then convert to float.

def parse_precio(val):
    if pd.isna(val):
        return None
    # Convert to string in case
    s = str(val).strip()
    # Remove dots used as thousand separator, and commas (if any)
    # Some values could be "599.000" -> "599000"
    # some could be "1.399" which is 1399? But in target example line 35: 1.399 means 1399 and it is int.
    # So remove dots, then convert to float
    s_clean = s.replace('.', '').replace(',', '.')
    try:
        return float(s_clean)
    except:
        return None

df_all['precio'] = df_all['precio'].apply(parse_precio)

# 2. Ensure string columns are of type str (some might have NaNs)
str_cols = ['titulo', 'tipo', 'condicion', 'ubicacion', 'tiempo', 'reputacion', 'pago']
for c in str_cols:
    df_all[c] = df_all[c].astype(str).replace('nan', pd.NA)

# 3. Some columns 'condicion' have format like 'Nuevo  -  177 vendidos'.
# Target example contains these full strings, so keep as-is.

# 4. 'tiempo' contains values like '12 Años', '4 Años', '11 Meses', and NaN.
# Target shows these values as is. So keep as str (already done).

# 5. 'reputacion' contains strings like "98% de compradores lo recomiendan" or NaN.
# Keep as-is as string.

# 6. 'pago' is string, contains values like "Efectivo" or "Tarjeta de Crédito" or NaN.
# Keep as-is.

# 7. Remove rows that contain NaN in any of the columns (to mimic target examples that mostly have those columns filled)
# However, the target examples do show some NaNs in 'reputacion' and 'pago', so we will keep those rows and not drop.
# So we will NOT drop any rows with NaN.

# 8. Reset index for output
df_all.reset_index(drop=True, inplace=True)

# 9. Reorder columns just in case to match target schema order
target_columns = ['titulo', 'tipo', 'precio', 'condicion', 'ubicacion', 'tiempo', 'reputacion', 'pago']
df_all = df_all[target_columns]

# Export the final dataframe to the given output path
output_path = 'autopipeline-benchmarks/github-pipelines/length4_86/target_multisource_cot.csv'
df_all.to_csv(output_path, index=False)