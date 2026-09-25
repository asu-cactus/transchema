import pandas as pd

df_students = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_76/training_0.csv", index_col=0)
df_schools = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_76/training_1.csv", index_col=0)

df_merged = pd.merge(df_students, df_schools, how="inner", on="school_name")

df_merged = df_merged[['Student ID', 'student_name', 'gender', 'grade', 'school_name', 'reading_score', 'math_score', 'School ID', 'type', 'size', 'budget']]

df_merged['Student ID'] = df_merged['Student ID'].astype(int)
df_merged['reading_score'] = df_merged['reading_score'].astype(int)
df_merged['math_score'] = df_merged['math_score'].astype(int)
df_merged['School ID'] = df_merged['School ID'].astype(int)
df_merged['size'] = df_merged['size'].astype(int)
df_merged['budget'] = df_merged['budget'].astype(int)

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_76/target_multisource_mcts.csv", index=False)