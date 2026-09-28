import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv", index_col=0)

pivot_df1 = df1.pivot(index='State', columns='Participation', values=['Evidence-Based Reading and Writing', 'Math', 'Total'])
pivot_df1.columns = [f"{col[0]}_{col[1]}" for col in pivot_df1.columns]
pivot_df1 = pivot_df1.reset_index()

participation_x = df0[['State', 'Participation']].rename(columns={'Participation': 'Participation_x'})
participation_y = df1[['State', 'Participation']].rename(columns={'Participation': 'Participation_y'})

merged = pd.merge(df0, participation_y, on='State', how='inner')
merged = merged.rename(columns={'Participation': 'Participation_x', 'Math': 'Math_x'})

merged = pd.merge(merged, df1, left_on=['State', 'Participation_y'], right_on=['State', 'Participation'], how='inner', suffixes=('', '_y'))
merged = merged.rename(columns={'Math': 'Math_y'})

result = merged[['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite', 'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv", index=False)