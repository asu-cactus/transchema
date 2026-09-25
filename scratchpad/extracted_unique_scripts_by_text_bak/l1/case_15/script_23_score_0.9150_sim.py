import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_1.csv", index_col=0)

agg1 = df1.groupby('State').agg({
    'Evidence-Based Reading and Writing': 'sum',
    'Math': 'sum',
    'Total': 'sum',
    'Participation': lambda x: ','.join(x.unique())
}).reset_index()

agg0 = df0.groupby(['State', 'Participation']).agg({
    'English': 'mean',
    'Math': 'mean',
    'Reading': 'mean',
    'Science': 'mean',
    'Composite': 'mean'
}).reset_index()

merged = pd.merge(agg0, agg1, on='State', how='inner', suffixes=('_x', '_y'))

merged.rename(columns={
    'Participation_x': 'Participation_x',
    'Participation_y': 'Participation_y',
    'Math_x': 'Math_x',
    'Math_y': 'Math_y',
    'Evidence-Based Reading and Writing': 'Evidence-Based Reading and Writing',
    'Total': 'Total',
    'English': 'English',
    'Reading': 'Reading',
    'Science': 'Science',
    'Composite': 'Composite'
}, inplace=True)

merged = merged[['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
                 'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']]

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_15/target_multisource_mcts.csv", index=False)