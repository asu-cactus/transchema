import pandas as pd

df_students = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_1/training_0.csv", index_col=0)
df_schools = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_1/training_1.csv", index_col=0)

agg = df_students.groupby('Student ID').agg({
    'student_name': 'first',
    'gender': 'first',
    'grade': 'first',
    'school_name': 'first',
    'reading_score': 'first',
    'math_score': 'first'
}).reset_index()

result = pd.merge(agg, df_schools, how='inner', on='school_name')

result = result.rename(columns={
    'Student ID': 'Student ID',
    'student_name': 'student_name',
    'gender': 'gender',
    'grade': 'grade',
    'school_name': 'school_name',
    'reading_score': 'reading_score',
    'math_score': 'math_score',
    'School ID': 'School ID',
    'type': 'type',
    'size': 'size',
    'budget': 'budget'
})

result = result[['Student ID', 'student_name', 'gender', 'grade', 'school_name', 'reading_score', 'math_score', 'School ID', 'type', 'size', 'budget']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_1/target_multisource_mcts.csv", index=False)