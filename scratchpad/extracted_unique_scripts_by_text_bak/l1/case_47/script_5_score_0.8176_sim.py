import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_47/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_47/training_1.csv", index_col=0)

df = pd.merge(df0, df1, on="school_name", how="left")

df = df[['Student ID', 'student_name', 'gender', 'grade', 'school_name', 'reading_score', 'math_score', 'School ID', 'type', 'size', 'budget']]

df['Student ID'] = df['Student ID'].astype(int)
df['reading_score'] = df['reading_score'].astype(int)
df['math_score'] = df['math_score'].astype(int)
df['School ID'] = df['School ID'].astype(int)
df['size'] = df['size'].astype(int)
df['budget'] = df['budget'].astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_47/target_multisource_mcts.csv", index=False)