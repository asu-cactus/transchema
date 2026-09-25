import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_2.csv", index_col=0)

agg = df0.groupby('school').agg(
    **{
        'Average Math Score': ('math_score', 'mean'),
        'Average Reading Score': ('reading_score', 'mean'),
        'Student Count': ('Student ID', 'count')
    }
).reset_index().rename(columns={'school': 'school'})

merged = pd.merge(agg, df2, how='inner', left_on='school', right_on='school')

final = pd.merge(merged, df1, how='inner', left_on='school', right_on='name')

result = pd.DataFrame()
result['School ID'] = final['School ID'].astype('Int64')
result['name'] = final['name']
result['type'] = final['type']
result['size'] = final['size'].astype('Int64')
result['budget'] = final['budget'].astype('Int64')
result['Average Math Score'] = final['Average Math Score_x'].astype(float)
result['Average Reading Score'] = final['Average Reading Score_x'].astype(float)
result['Number Passing Math'] = final['Number Passing Math'].astype('Int64')
result['Number Passing Reading'] = final['Number Passing Reading'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_77/target_multisource_mcts.csv", index=False)