import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_24/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_24/training_1.csv", index_col=0)

grouped = df0.groupby(['school_name', 'gender', 'grade']).agg(
    Student_ID_count=('Student ID', 'count'),
    math_score_avg=('math_score', 'mean'),
    reading_score_avg=('reading_score', 'mean')
).reset_index()

merged = pd.merge(grouped, df1[['school_name', 'type', 'budget']], how='inner', left_on='school_name', right_on='school_name')

result = merged[['school_name', 'Student_ID_count', 'budget', 'math_score_avg', 'reading_score_avg']]

result = result.rename(columns={
    'Student_ID_count': 'Student ID',
    'math_score_avg': 'math_score',
    'reading_score_avg': 'reading_score'
})

result['Student ID'] = result['Student ID'].astype(int)
result['budget'] = result['budget'].astype(int)
result['math_score'] = result['math_score'].astype(float)
result['reading_score'] = result['reading_score'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_24/target_multisource_mcts.csv", index=False)