import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_1.csv", index_col=0)

agg0 = df0.groupby('Participation').agg({
    'English': 'mean',
    'Math': 'mean',
    'Reading': 'mean',
    'Science': 'mean',
    'Composite': 'mean'
}).reset_index()

agg1 = df1.groupby('Participation').agg({
    'Evidence-Based Reading and Writing': 'mean',
    'Math': 'mean',
    'Total': 'mean'
}).reset_index()

merged = pd.merge(agg0, agg1, on='Participation', suffixes=('_x', '_y'))

merged = merged.rename(columns={
    'Participation': 'Participation_y',
    'Participation_x': 'Participation_x',
    'English': 'English',
    'Math_x': 'Math_x',
    'Reading': 'Reading',
    'Science': 'Science',
    'Composite': 'Composite',
    'Evidence-Based Reading and Writing': 'Evidence-Based Reading and Writing',
    'Math_y': 'Math_y',
    'Total': 'Total'
})

merged['Participation_x'] = merged['Participation_y']  # Participation_x is same as Participation_y in target examples

merged['Evidence-Based Reading and Writing'] = merged['Evidence-Based Reading and Writing'].round().astype('Int64')
merged['Math_y'] = merged['Math_y'].round().astype('Int64')
merged['Total'] = merged['Total'].round().astype('Int64')

merged = merged[['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite', 'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']] if 'State' in merged.columns else merged

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_15/target_multisource_mcts.csv", index=False)