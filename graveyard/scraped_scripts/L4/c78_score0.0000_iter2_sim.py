import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_2.csv", index_col=0)

agg = source2.groupby('school').agg(
    Average_Math_Score=('math_score', 'mean'),
    Average_Reading_Score=('reading_score', 'mean'),
    Number_Passing_Math=('math_score', lambda x: (x >= 70).sum()),
    Number_Passing_Reading=('reading_score', lambda x: (x >= 70).sum())
).reset_index()

join1 = pd.merge(source1, agg, left_on='name', right_on='school', how='inner')
join2 = pd.merge(join1, source0, left_on='name', right_on='school', how='inner')

result = join2.rename(columns={
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

result['School Size'] = result['size']

final_cols = ['School ID', 'name', 'type', 'size', 'budget', 'Average Math Score', 'Average Reading Score',
              'Number Passing Math', 'Number Passing Reading', 'School Size']

result = result[final_cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_78/target_multisource_mcts.csv", index=False)