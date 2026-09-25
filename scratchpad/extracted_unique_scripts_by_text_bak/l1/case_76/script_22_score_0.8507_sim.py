import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_76/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_76/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="school_name", how="inner")

merged = merged[['Student ID', 'student_name', 'gender', 'grade', 'school_name', 'reading_score', 'math_score', 'School ID', 'type', 'size', 'budget']]

merged['Student ID'] = merged['Student ID'].astype(int)
merged['reading_score'] = merged['reading_score'].astype(int)
merged['math_score'] = merged['math_score'].astype(int)
merged['School ID'] = merged['School ID'].astype(int)
merged['size'] = merged['size'].astype(int)
merged['budget'] = merged['budget'].astype(int)
merged['student_name'] = merged['student_name'].astype(str)
merged['gender'] = merged['gender'].astype(str)
merged['grade'] = merged['grade'].astype(str)
merged['school_name'] = merged['school_name'].astype(str)
merged['type'] = merged['type'].astype(str)

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_76/target_multisource_mcts.csv", index=False)