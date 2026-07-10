import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv", index_col=0)

union_df = pd.concat([df0, df0], ignore_index=True)

merged = pd.merge(union_df, df1, on="State", suffixes=('_x', '_y'))

result = pd.DataFrame()
result['State'] = merged['State']
result['Participation_x'] = merged['Participation_x']
result['English'] = merged['English'].astype(float)
result['Math_x'] = merged['Math_x'].astype(float)
result['Reading'] = merged['Reading'].astype(float)
result['Science'] = merged['Science'].astype(float)
result['Composite'] = merged['Composite'].astype(float)
result['Participation_y'] = merged['Participation_y']
result['Evidence-Based Reading and Writing'] = merged['Evidence-Based Reading and Writing'].astype('Int64')
result['Math_y'] = merged['Math_y'].astype('Int64')
result['Total'] = merged['Total'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv", index=False)