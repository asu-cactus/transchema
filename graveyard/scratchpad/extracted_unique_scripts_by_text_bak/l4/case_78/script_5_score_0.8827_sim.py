import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_2.csv", index_col=0)

# Unpivot df1 for columns 'type', 'size', 'budget' is not needed because these are separate columns in target schema.
# Instead, we keep df1 as is.

# Join df0 and df1 on school name
merged = pd.merge(df1, df0, left_on='name', right_on='school', how='inner')

# Calculate School Size from df1 'size' column (already present)
# Group by School ID, name, type, size, budget and aggregate scores and passing counts
agg = merged.groupby(['School ID', 'name', 'type', 'size', 'budget'], as_index=False).agg({
    'Average Math Score': 'mean',
    'Average Reading Score': 'mean',
    'Number Passing Math': 'sum',
    'Number Passing Reading': 'sum'
})

# Add School Size column same as size
agg['School Size'] = agg['size']

# Ensure correct dtypes
agg = agg.astype({
    'School ID': 'int64',
    'name': 'string',
    'type': 'string',
    'size': 'int64',
    'budget': 'int64',
    'Average Math Score': 'float64',
    'Average Reading Score': 'float64',
    'Number Passing Math': 'int64',
    'Number Passing Reading': 'int64',
    'School Size': 'int64'
})

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_78/target_multisource_mcts.csv", index=False)