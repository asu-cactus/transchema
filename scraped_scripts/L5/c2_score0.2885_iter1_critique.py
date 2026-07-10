import pandas as pd

# Read sources
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_4.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_5.csv", index_col=0)

# Rename business/count columns in each source to match target schema
src0_renamed = src0.rename(columns={
    'businesses': 'businesses_x_5',
    'counts': 'counts_x_6'
})

src2_renamed = src2.rename(columns={
    'businesses': 'businesses_y',
    'counts': 'counts_y'
})

src3_renamed = src3.rename(columns={
    'businesses': 'businesses_y_7',
    'counts': 'counts_y_8'
})

src4_renamed = src4.rename(columns={
    'businesses': 'businesses_x',
    'counts': 'counts_x'
})

# Start joining on zipcode
df = pd.merge(src4_renamed, src2_renamed, on='zipcode', how='outer')
df = pd.merge(df, src0_renamed, on='zipcode', how='outer')
df = pd.merge(df, src3_renamed, on='zipcode', how='outer')

# Add boro from src1
df = pd.merge(df, src1, on='zipcode', how='left')

# Add businesses (integer) from src5
df = pd.merge(df, src5.rename(columns={'businesses': 'businesses'}), on='zipcode', how='left')

# Ensure correct dtypes and fill missing counts with 0
for col in ['counts_x', 'counts_y', 'counts_x_6', 'counts_y_8', 'businesses']:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

# Convert business name columns and boro to string dtype
for col in ['businesses_x', 'businesses_y', 'businesses_x_5', 'businesses_y_7', 'boro']:
    df[col] = df[col].astype('string')

# Group by the leftmost unique keys and business name columns (strings), aggregate counts by sum
group_cols = ['zipcode', 'boro', 'businesses_x', 'businesses_y', 'businesses_x_5', 'businesses_y_7']
agg_dict = {
    'counts_x': 'sum',
    'counts_y': 'sum',
    'counts_x_6': 'sum',
    'counts_y_8': 'sum',
    'businesses': 'sum'
}

df = df.groupby(group_cols, dropna=False, as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
df = df[['zipcode', 'businesses_x', 'counts_x', 'businesses_y', 'counts_y',
         'businesses_x_5', 'counts_x_6', 'businesses_y_7', 'counts_y_8', 'boro', 'businesses']]

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length5_2/target_multisource_mcts.csv", index=False)