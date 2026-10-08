import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_95/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_95/training_1.csv", index_col=0)

pivot = df1.pivot_table(index=['school', 'grade', 'Student ID'], 
                        values=['reading_score', 'math_score'], 
                        aggfunc={'reading_score':'mean', 'math_score':'mean'}).reset_index()

pivot = pivot.rename(columns={
    'school': 'School Name',
    'grade': 'Student Grade',
    'Student ID': 'Student ID',
    'reading_score': 'Student Reading Score',
    'math_score': 'Average Student Math Score'
})

df0_renamed = df0.rename(columns={
    'name': 'School Name',
    'type': 'School Type',
    'size': 'School Size',
    'budget': 'School Budget',
    'School ID': 'School ID'
})

merged = pd.merge(pivot, df0_renamed[['School Name', 'School ID', 'School Size', 'School Budget']], on='School Name', how='left')

merged = merged[['School Name', 'Student Grade', 'School ID', 'School Size', 'School Budget', 'Student ID', 'Student Reading Score', 'Average Student Math Score']]

merged['School ID'] = merged['School ID'].astype('Int64')
merged['School Size'] = merged['School Size'].astype('Int64')
merged['School Budget'] = merged['School Budget'].astype('Int64')
merged['Student ID'] = merged['Student ID'].astype(float)
merged['Student Reading Score'] = merged['Student Reading Score'].astype(float)
merged['Average Student Math Score'] = merged['Average Student Math Score'].astype(float)
merged['Student Grade'] = merged['Student Grade'].astype(str)
merged['School Name'] = merged['School Name'].astype(str)

merged.to_csv("autopipeline-benchmarks/github-pipelines/length2_95/target_multisource_mcts.csv", index=False)