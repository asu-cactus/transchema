import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_33/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_33/training_1.csv", index_col=0)

agg = df1.groupby(['State', 'Participation'], as_index=False).agg({
    'Evidence-Based Reading and Writing': 'sum',
    'Math': 'sum',
    'Total': 'sum'
}).rename(columns={'Participation': 'Participation_y', 'Math': 'Math_y'})

merged = pd.merge(df0, agg, how='inner', left_on=['State', 'Participation'], right_on=['State', 'Participation_y'])

result = merged.rename(columns={
    'Participation_x': 'Participation',
    'Participation': 'Participation_x'
})

result = result.rename(columns={
    'Participation_x': 'Participation_x',
    'Participation_y': 'Participation_y'
})

result = result.rename(columns={
    'Math': 'Math_x'
})

result = result[['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite', 'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_33/target_multisource_mcts.csv", index=False)