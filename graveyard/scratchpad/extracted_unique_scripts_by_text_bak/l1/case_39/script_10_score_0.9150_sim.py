import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv", index_col=0)

agg0 = df0.groupby('State').agg({
    'English': 'mean',
    'Math': 'mean',
    'Reading': 'mean',
    'Science': 'mean',
    'Composite': 'mean',
    'Participation': 'max'
}).rename(columns={'Participation': 'Participation_x', 'Math': 'Math_x'}).reset_index()

agg1 = df1.groupby('State').agg({
    'Participation': 'max',
    'Evidence-Based Reading and Writing': 'max',
    'Math': 'max',
    'Total': 'max'
}).rename(columns={'Participation': 'Participation_y', 'Math': 'Math_y'}).reset_index()

merged = pd.merge(agg0, agg1, on='State', how='inner')

merged['Evidence-Based Reading and Writing'] = merged['Evidence-Based Reading and Writing'].astype('Int64')
merged['Total'] = merged['Total'].astype('Int64')

result = merged[['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
                 'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv", index=False)