import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_2.csv", index_col=0)

agg_df = df0.groupby('school').agg(
    Number_Passing_Math = ('math_score', lambda x: (x >= 60).sum()),
    Number_Passing_Reading = ('reading_score', lambda x: (x >= 60).sum()),
    Total_Math_Score = ('math_score', 'sum'),
    Total_Reading_Score = ('reading_score', 'sum'),
    Student_Count = ('Student ID', 'count')
).reset_index()

merged = pd.merge(agg_df, df1, left_on='school', right_on='name', how='inner')

merged['Average Math Score'] = merged['Total_Math_Score'] / merged['Student_Count']
merged['Average Reading Score'] = merged['Total_Reading_Score'] / merged['Student_Count']

result = merged.rename(columns={
    'school': 'name',
    'School ID': 'School ID',
    'type': 'type',
    'size': 'size',
    'budget': 'budget',
    'Number_Passing_Math': 'Number Passing Math',
    'Number_Passing_Reading': 'Number Passing Reading'
})[['School ID', 'name', 'type', 'size', 'budget', 'Average Math Score', 'Average Reading Score', 'Number Passing Math', 'Number Passing Reading']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_77/target_multisource_mcts.csv", index=False)