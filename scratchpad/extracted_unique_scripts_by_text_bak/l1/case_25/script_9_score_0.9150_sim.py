import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_25/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_25/training_1.csv", index_col=0)

pivot_df0 = df0.rename(columns={
    'Participation': 'Participation_x',
    'Math': 'Math_x'
})

merged = pd.merge(
    pivot_df0,
    df1.rename(columns={'Participation': 'Participation_y', 'Math': 'Math_y'}),
    on='State',
    how='inner'
)

cols = ['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
        'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']

result = merged[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_25/target_multisource_mcts.csv", index=False)