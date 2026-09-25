import pandas as pd

# Read all source files
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_70/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_70/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_70/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_70/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_70/training_4.csv", index_col=0)

# Concatenate all sources (UNION)
df = pd.concat([src0, src1, src2, src3, src4], ignore_index=True)

# Ensure correct dtypes for grouping columns
df['GEO.id'] = df['GEO.id'].astype(str)
df['GEO.id2'] = df['GEO.id2'].astype(str)
df['GEO.display-label'] = df['GEO.display-label'].astype(str)
df['Year'] = df['Year'].astype(int)

# Convert HD01_VD01 and HD02_VD01 to numeric for aggregation (coerce errors to NaN)
df['HD01_VD01'] = pd.to_numeric(df['HD01_VD01'], errors='coerce')
df['HD02_VD01'] = pd.to_numeric(df['HD02_VD01'], errors='coerce')

# Group by key columns and sum the numeric columns
agg_df = df.groupby(['GEO.id', 'GEO.id2', 'GEO.display-label', 'Year'], as_index=False).agg({
    'HD01_VD01': 'sum',
    'HD02_VD01': 'sum'
})

# Convert aggregated numeric columns back to string to match target schema
agg_df['HD01_VD01'] = agg_df['HD01_VD01'].astype(str)
agg_df['HD02_VD01'] = agg_df['HD02_VD01'].astype(str)

# Reorder columns to match target schema exactly
agg_df = agg_df[['GEO.id', 'GEO.id2', 'GEO.display-label', 'HD01_VD01', 'HD02_VD01', 'Year']]

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_70/target_multisource_mcts.csv", index=False)