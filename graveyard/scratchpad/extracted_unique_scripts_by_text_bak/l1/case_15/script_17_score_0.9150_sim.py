import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_1.csv", index_col=0)

agg0 = df0.groupby(['State', 'Participation'], as_index=False).agg({
    'English': 'sum',
    'Math': 'sum',
    'Reading': 'sum',
    'Science': 'sum',
    'Composite': 'sum'
})

agg1 = df1.groupby(['State', 'Participation'], as_index=False).agg({
    'Evidence-Based Reading and Writing': 'sum',
    'Math': 'sum',
    'Total': 'sum'
})

merged = pd.merge(agg0, agg1, on='State', suffixes=('_x', '_y'))

merged.rename(columns={
    'Participation_x': 'Participation_x',
    'Participation_y': 'Participation_y',
    'Math_x': 'Math_x',
    'Math_y': 'Math_y'
}, inplace=True)

merged = merged[['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
                 'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']]

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_15/target_multisource_mcts.csv", index=False)