import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_8/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_8/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_8/training_3.csv", index_col=0)

# Join Source0 and Source1 on COD_OFICIPAL=COD_OFICI and COD_AREANEGO=cod_areanego
# First, ensure cod_areanego in df1 is same type as COD_AREANEGO in df0
# cod_areanego in df1 may have NaNs, so drop rows with NaN in cod_areanego before join
df1_filtered = df1.dropna(subset=['cod_areanego']).copy()
df1_filtered['cod_areanego'] = df1_filtered['cod_areanego'].astype(int)

df01 = pd.merge(
    df0,
    df1_filtered,
    left_on=['COD_OFICIPAL', 'COD_AREANEGO'],
    right_on=['COD_OFICI', 'cod_areanego'],
    how='inner'
)

# Join Source2 and Source3 on COD_PERSONA and COD_IDCONTRA
df23 = pd.merge(
    df2,
    df3,
    on=['COD_PERSONA', 'COD_IDCONTRA'],
    how='inner'
)

# Join the two joined tables on COD_PERSONA
df_final = pd.merge(
    df01,
    df23,
    on='COD_PERSONA',
    how='inner'
)

# Select and rename columns to match target schema
# Target schema: ['des_zona': string, 'COD_PERSONA_x': integer, 'COD_AREANEGO': integer]
result = df_final[['des_zona', 'COD_PERSONA', 'COD_AREANEGO']].copy()
result.rename(columns={'COD_PERSONA': 'COD_PERSONA_x'}, inplace=True)

# Group by all three columns to ensure uniqueness (no aggregation needed)
result = result.drop_duplicates()

# Ensure correct dtypes
result['des_zona'] = result['des_zona'].astype(str)
result['COD_PERSONA_x'] = result['COD_PERSONA_x'].astype(int)
result['COD_AREANEGO'] = result['COD_AREANEGO'].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_8/target_multisource_mcts.csv", index=False)