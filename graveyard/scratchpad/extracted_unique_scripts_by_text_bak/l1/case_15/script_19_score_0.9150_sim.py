import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_1.csv", index_col=0)

grouped = df0.groupby(['State', 'Participation'], as_index=False).agg({
    'English': 'mean',
    'Math': 'mean',
    'Reading': 'mean',
    'Science': 'mean',
    'Composite': 'mean'
})

merged = pd.merge(grouped, df1, on='State', how='inner', suffixes=('_x', '_y'))

result = merged.rename(columns={
    'Participation_x': 'Participation_x',
    'English': 'English',
    'Math_x': 'Math_x',
    'Reading': 'Reading',
    'Science': 'Science',
    'Composite': 'Composite',
    'Participation_y': 'Participation_y',
    'Evidence-Based Reading and Writing': 'Evidence-Based Reading and Writing',
    'Math_y': 'Math_y',
    'Total': 'Total'
})[
    ['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
     'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']
]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_15/target_multisource_mcts.csv", index=False)