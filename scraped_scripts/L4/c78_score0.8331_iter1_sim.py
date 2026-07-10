import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_78/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_78/training_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_78/training_2.csv', index_col=0)

df2_agg = df2.groupby('school').agg({
    'math_score': 'mean',
    'reading_score': 'mean'
}).rename(columns={
    'math_score': 'Average Math Score',
    'reading_score': 'Average Reading Score'
}).reset_index()

df0_renamed = df0.rename(columns={'school': 'school'})

df0_agg = df0_renamed.copy()

union_result = pd.concat([df0_agg, df2_agg], axis=0, ignore_index=True, sort=False)

union_result = union_result.groupby('school', as_index=False).agg({
    'Average Math Score': 'mean',
    'Average Reading Score': 'mean',
    'Number Passing Math': 'sum',
    'Number Passing Reading': 'sum'
})

merged = pd.merge(union_result, df1, left_on='school', right_on='name', how='inner')

result = merged.groupby(['School ID', 'name', 'type', 'size', 'budget'], as_index=False).agg({
    'Average Math Score': 'mean',
    'Average Reading Score': 'mean',
    'Number Passing Math': 'sum',
    'Number Passing Reading': 'sum'
})

result['School Size'] = result['size']

result = result.astype({
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

result.to_csv('autopipeline-benchmarks/github-pipelines/length4_78/target_multisource_mcts.csv', index=False)