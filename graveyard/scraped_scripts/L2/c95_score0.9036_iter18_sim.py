import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_95/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_95/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_95/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

agg = df1.groupby(['school', 'grade']).agg({
    'Student ID': 'sum',
    'reading_score': 'min',
    'math_score': 'max'
}).reset_index()

merged = pd.merge(df0, agg, left_on='name', right_on='school', how='inner')

result = merged.rename(columns={
    'name': 'School Name',
    'grade': 'Student Grade',
    'School ID': 'School ID',
    'size': 'School Size',
    'budget': 'School Budget',
    'Student ID': 'Student ID',
    'reading_score': 'Student Reading Score',
    'math_score': 'Average Student Math Score',
    'school': 'school'  # will drop later
})

result = result[['School Name', 'Student Grade', 'School ID', 'School Size', 'School Budget', 'Student ID', 'Student Reading Score', 'Average Student Math Score']]

result = result.astype({
    'School Name': str,
    'Student Grade': str,
    'School ID': int,
    'School Size': int,
    'School Budget': int,
    'Student ID': float,
    'Student Reading Score': float,
    'Average Student Math Score': float
})

result.to_csv(target_path, index=False)