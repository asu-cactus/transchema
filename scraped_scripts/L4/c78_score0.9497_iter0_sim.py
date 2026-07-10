import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_2.csv", index_col=0)

agg = source2.groupby('school').agg(
    **{
        'Average Math Score': ('math_score', 'mean'),
        'Average Reading Score': ('reading_score', 'mean'),
        'Number Passing Math': ('math_score', lambda x: (x >= 70).sum()),
        'Number Passing Reading': ('reading_score', lambda x: (x >= 70).sum()),
        'School Size': ('Student ID', 'count')
    }
).reset_index()

join1 = pd.merge(source1, agg, left_on='name', right_on='school', how='inner')

final = pd.merge(join1, source0, left_on='name', right_on='school', how='inner')

final = final.rename(columns={
    'School ID': 'School ID',
    'name': 'name',
    'type': 'type',
    'size': 'size',
    'budget': 'budget',
    'Average Math Score_x': 'Average Math Score',
    'Average Reading Score_x': 'Average Reading Score',
    'Number Passing Math_x': 'Number Passing Math',
    'Number Passing Reading_x': 'Number Passing Reading',
    'School Size': 'School Size'
})

final = final[['School ID', 'name', 'type', 'size', 'budget', 'Average Math Score', 'Average Reading Score', 'Number Passing Math', 'Number Passing Reading', 'School Size']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_78/target_multisource_mcts.csv", index=False)