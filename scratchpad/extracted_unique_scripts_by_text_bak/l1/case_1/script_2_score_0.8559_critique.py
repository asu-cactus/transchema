import pandas as pd

df_students = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_1/training_0.csv", index_col=0)
df_schools = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_1/training_1.csv", index_col=0)

result = pd.merge(df_students, df_schools, how='inner', on='school_name')

result = result[['Student ID', 'student_name', 'gender', 'grade', 'school_name', 'reading_score', 'math_score',
                 'School ID', 'type', 'size', 'budget']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_1/target_multisource_mcts.csv", index=False)