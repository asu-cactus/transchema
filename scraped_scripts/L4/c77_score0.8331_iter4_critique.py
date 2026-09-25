import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_2.csv", index_col=0)

# Join df1 and df2 on school name
merged = pd.merge(df1, df2, left_on='name', right_on='school', how='inner')

# Select and rename columns to match target schema exactly
result = merged.rename(columns={
    'School ID': 'School ID',
    'name': 'name',
    'type': 'type',
    'size': 'size',
    'budget': 'budget',
    'Average Math Score': 'Average Math Score',
    'Average Reading Score': 'Average Reading Score',
    'Number Passing Math': 'Number Passing Math',
    'Number Passing Reading': 'Number Passing Reading'
})

result = result[['School ID', 'name', 'type', 'size', 'budget', 'Average Math Score', 'Average Reading Score', 'Number Passing Math', 'Number Passing Reading']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_77/target_multisource_mcts.csv", index=False)