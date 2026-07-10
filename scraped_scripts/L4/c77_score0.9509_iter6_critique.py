import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_2.csv", index_col=0)

# Join Source4_77_1 and Source4_77_2 on school name
join1 = pd.merge(df1, df2, left_on='name', right_on='school', how='inner')

# Join the above result with Source4_77_0 on school name to ensure usage of all source tables
join2 = pd.merge(join1, df0[['school']], left_on='name', right_on='school', how='inner')

# Group by the leftmost columns of the target schema (School ID, name, type, size, budget)
# Aggregate the numeric columns from Source4_77_2 by mean (safe since they are unique per school)
result = join2.groupby(['School ID', 'name', 'type', 'size', 'budget'], as_index=False).agg({
    'Average Math Score': 'mean',
    'Average Reading Score': 'mean',
    'Number Passing Math': 'mean',
    'Number Passing Reading': 'mean'
})

# Cast columns to correct types as per target schema
result['School ID'] = result['School ID'].astype(int)
result['name'] = result['name'].astype(str)
result['type'] = result['type'].astype(str)
result['size'] = result['size'].astype(int)
result['budget'] = result['budget'].astype(int)
result['Average Math Score'] = result['Average Math Score'].astype(float)
result['Average Reading Score'] = result['Average Reading Score'].astype(float)
result['Number Passing Math'] = result['Number Passing Math'].round().astype(int)
result['Number Passing Reading'] = result['Number Passing Reading'].round().astype(int)

# Write to output CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_77/target_multisource_mcts.csv", index=False)