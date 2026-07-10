import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_58/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_58/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="State", suffixes=('_x', '_y'))

result = merged.rename(columns={
    'Participation_x': 'Participation_x',
    'Participation_y': 'Participation_y',
    'Evidence-Based Reading and Writing': 'Evidence-Based Reading and Writing',
    'Math_x': 'Math_x',
    'Total': 'Total',
    'English': 'English',
    'Math_y': 'Math_y',
    'Reading': 'Reading',
    'Science': 'Science',
    'Composite': 'Composite'
})[
    ['State', 'Participation_x', 'Evidence-Based Reading and Writing', 'Math_x', 'Total',
     'Participation_y', 'English', 'Math_y', 'Reading', 'Science', 'Composite']
]

result['Evidence-Based Reading and Writing'] = result['Evidence-Based Reading and Writing'].astype('Int64')
result['Math_x'] = result['Math_x'].astype('Int64')
result['Total'] = result['Total'].astype('Int64')
result['English'] = result['English'].astype(float)
result['Math_y'] = result['Math_y'].astype(float)
result['Reading'] = result['Reading'].astype(float)
result['Science'] = result['Science'].astype(float)
result['Composite'] = result['Composite'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_58/target_multisource_mcts.csv", index=False)