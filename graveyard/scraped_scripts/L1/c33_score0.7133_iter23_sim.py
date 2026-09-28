import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_33/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_33/training_1.csv", index_col=0)

union_df = pd.concat([df0, df0], ignore_index=True)

merged = pd.merge(union_df, df1, on="State", suffixes=('_x', '_y'))

merged = merged.rename(columns={
    'Participation_x': 'Participation_x',
    'Participation_y': 'Participation_y',
    'English': 'English',
    'Math_x': 'Math_x',
    'Reading': 'Reading',
    'Science': 'Science',
    'Composite': 'Composite',
    'Evidence-Based Reading and Writing': 'Evidence-Based Reading and Writing',
    'Math_y': 'Math_y',
    'Total': 'Total'
})

cols = ['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
        'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']

result = merged[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_33/target_multisource_mcts.csv", index=False)