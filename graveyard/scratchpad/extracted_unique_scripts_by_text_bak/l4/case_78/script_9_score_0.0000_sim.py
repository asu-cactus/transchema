import pandas as pd
import numpy as np

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_2.csv", index_col=0)

source2['pass_math'] = (source2['math_score'] >= 60).astype(int)
source2['pass_reading'] = (source2['reading_score'] >= 60).astype(int)

agg = source2.groupby('school').agg(
    Average_Math_Score=('math_score', 'mean'),
    Average_Reading_Score=('reading_score', 'mean'),
    Number_Students=('Student ID', 'count'),
    Number_Passing_Math=('pass_math', 'sum'),
    Number_Passing_Reading=('pass_reading', 'sum')
).reset_index()

join1 = pd.merge(source1, agg, left_on='name', right_on='school', how='inner')

final = pd.merge(join1, source0, left_on='name', right_on='school', how='inner')

result = final.rename(columns={
    'School ID': 'School ID',
    'name': 'name',
    'type': 'type',
    'size': 'size',
    'budget': 'budget',
    'Average_Math_Score': 'Average Math Score',
    'Average_Reading_Score': 'Average Reading Score',
    'Number_Passing_Math': 'Number Passing Math',
    'Number_Passing_Reading': 'Number Passing Reading',
    'size': 'School Size'
})

result = result[['School ID', 'name', 'type', 'size', 'budget',
                 'Average Math Score', 'Average Reading Score',
                 'Number Passing Math', 'Number Passing Reading', 'size']]

result = result.rename(columns={'size': 'School Size'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_78/target_multisource_mcts.csv", index=False)