import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_51/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_51/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_51/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

df = pd.merge(df0, df1, on="school_name", how="inner")

df = df[['Student ID', 'student_name', 'gender', 'grade', 'school_name', 'reading_score', 'math_score', 'School ID', 'type', 'size', 'budget']]

df['Student ID'] = df['Student ID'].astype(int)
df['reading_score'] = df['reading_score'].astype(int)
df['math_score'] = df['math_score'].astype(int)
df['School ID'] = df['School ID'].astype(int)
df['size'] = df['size'].astype(int)
df['budget'] = df['budget'].astype(int)

df.to_csv(target_path, index=False)