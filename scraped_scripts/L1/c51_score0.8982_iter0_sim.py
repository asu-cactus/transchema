import pandas as pd

df_students = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_51/training_0.csv", index_col=0)
df_schools = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_51/training_1.csv", index_col=0)

agg = df_students.groupby('Student ID').agg({
    'student_name': 'first',
    'gender': 'first',
    'grade': 'first',
    'school_name': 'first',
    'reading_score': 'first',
    'math_score': 'first'
}).reset_index()

result = pd.merge(agg, df_schools, how='inner', on='school_name')

result = result[['Student ID', 'student_name', 'gender', 'grade', 'school_name', 'reading_score', 'math_score', 'School ID', 'type', 'size', 'budget']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_51/target_multisource_mcts.csv", index=False)