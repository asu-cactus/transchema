import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_76/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_76/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="school_name", how="left")

merged = merged[['Student ID', 'student_name', 'gender', 'grade', 'school_name', 'reading_score', 'math_score', 'School ID', 'type', 'size', 'budget']]

merged['Student ID'] = merged['Student ID'].astype('int64')
merged['reading_score'] = merged['reading_score'].astype('int64')
merged['math_score'] = merged['math_score'].astype('int64')
merged['School ID'] = merged['School ID'].astype('int64')
merged['size'] = merged['size'].astype('int64')
merged['budget'] = merged['budget'].astype('int64')

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_76/target_multisource_mcts.csv", index=False)