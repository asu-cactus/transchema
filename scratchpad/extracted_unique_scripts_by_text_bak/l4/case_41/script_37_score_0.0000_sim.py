import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

dfs = [s0, s1, s2, s3]

for i, df in enumerate(dfs):
    df.columns = ['x', 'y', 'label']

merged = dfs[0]
for df in dfs[1:]:
    merged = pd.merge(merged, df, on='y', suffixes=('', '_dup'))
    # Remove duplicate columns after merge
    dup_cols = [c for c in merged.columns if c.endswith('_dup')]
    merged.drop(columns=dup_cols, inplace=True)

# After join, columns: y, x, label from each source but merged into one set of columns (x, label) from first source only
# This is not correct because we lose other x,label columns from other sources.
# Instead, we should join all sources on 'y' keeping their x and label columns distinct.

# Re-do join properly to keep all x and label columns from each source with distinct names
s0_renamed = s0.rename(columns={'x':'x_0', 'label':'label_0'})
s1_renamed = s1.rename(columns={'x':'x_1', 'label':'label_1'})
s2_renamed = s2.rename(columns={'x':'x_2', 'label':'label_2'})
s3_renamed = s3.rename(columns={'x':'x_3', 'label':'label_3'})

merged = s0_renamed.merge(s1_renamed, on='y').merge(s2_renamed, on='y').merge(s3_renamed, on='y')

# Now pivot: we want to convert columns x_0,label_0,x_1,label_1,... into rows with columns y,x,label
# We can stack the data from each source into one dataframe

parts = []
for i in range(4):
    part = merged[['y', f'x_{i}', f'label_{i}']].copy()
    part.columns = ['y', 'x', 'label']
    parts.append(part)

result = pd.concat(parts, ignore_index=True)

# Convert types: y float, x int, label int
result['y'] = result['y'].astype(float)
result['x'] = pd.to_numeric(result['x'], errors='coerce').astype('Int64')
# label is string in sources, convert to integer codes
result['label'] = result['label'].astype('category').cat.codes.astype('Int64')

result = result[['y', 'x', 'label']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)