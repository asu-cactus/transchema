import pandas as pd

# Load source data with index_col=0 to ignore the first numerical index column
source_0 = pd.read_csv('/home/local/ASUAD/jrtandel/transchema/autopipeline-benchmarks/github-pipelines/length4_36/test_0.csv', index_col=0)
source_1 = pd.read_csv('/home/local/ASUAD/jrtandel/transchema/autopipeline-benchmarks/github-pipelines/length4_36/test_1.csv', index_col=0)
source_2 = pd.read_csv('/home/local/ASUAD/jrtandel/transchema/autopipeline-benchmarks/github-pipelines/length4_36/test_2.csv', index_col=0)
source_3 = pd.read_csv('/home/local/ASUAD/jrtandel/transchema/autopipeline-benchmarks/github-pipelines/length4_36/test_3.csv', index_col=0)
source_4 = pd.read_csv('/home/local/ASUAD/jrtandel/transchema/autopipeline-benchmarks/github-pipelines/length4_36/test_4.csv', index_col=0)

# Step 1: Join Source4_36_2 with Source4_36_0 on IdCausa to add Causa
df = source_2.merge(source_0[['IdCausa', 'Causa']], how='inner', on='IdCausa')

# Step 2: Join the result with Source4_36_1 on IdDeteccion to add Deteccion
df = df.merge(source_1[['IdDeteccion', 'Deteccion']], how='inner', on='IdDeteccion')

# Step 3: Join the result with Source4_36_3 on IdActividad to add Actividad
df = df.merge(source_3[['IdActividad', 'Actividad']], how='inner', on='IdActividad')

# Step 4: Join the result with Source4_36_4 on IdFactor to add Factor
df = df.merge(source_4[['IdFactor', 'Factor']], how='inner', on='IdFactor')

# Step 5: Project all columns to match Target4_36 schema
# The target schema is assumed to be all columns from source_2 plus the joined descriptive columns:
# Columns from source_2 except the foreign key columns replaced by descriptive columns:
# Keep all original columns from source_2 except IdCausa, IdDeteccion, IdActividad, IdFactor
# Add Causa, Deteccion, Actividad, Factor columns

# Identify columns to keep from source_2 (all except the four ID columns)
cols_to_keep = [col for col in source_2.columns if col not in ['IdCausa', 'IdDeteccion', 'IdActividad', 'IdFactor']]

# Final columns order: all cols_to_keep + Causa, Deteccion, Actividad, Factor
final_columns = cols_to_keep + ['Causa', 'Deteccion', 'Actividad', 'Factor']

df_final = df[final_columns]

# Step 6: Save the final dataframe to CSV
output_path = '/home/local/ASUAD/jrtandel/transchema/autopipeline-benchmarks/github-pipelines/length4_36/target_multisource_agentic.csv'
df_final.to_csv(output_path, index=False)