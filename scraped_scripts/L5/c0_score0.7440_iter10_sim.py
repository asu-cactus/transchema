import pandas as pd
import numpy as np

source0_path = "autopipeline-benchmarks/github-pipelines/length5_0/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length5_0/training_1.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length5_0/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

df1['grade'] = df1['grade'].str.extract('(\d+)').astype(int)
df1['gender'] = df1['gender'].map({'F': 1, 'M': 0}).fillna(0).astype(int)

agg_df = df1.groupby('school_name').agg(
    Total_Students=('student_name', 'count'),
    Average_Reading_Score=('reading_score', 'mean'),
    Average_Math_Score=('math_score', 'mean'),
    Total_Passing_Math=('math_score', lambda x: (x >= 70).sum()),
    Total_Passing_Reading=('reading_score', lambda x: (x >= 70).sum()),
    gender=('gender', 'first'),
    grade=('grade', 'first'),
    student_name=('student_name', 'count')
).reset_index()

merged = pd.merge(agg_df, df0, left_on='school_name', right_on='school_name', how='inner')

merged.rename(columns={
    'school_name': 'School Name',
    'type': 'School Type',
    'size': 'size',
    'budget': 'Total Budget',
    'student_name': 'student_name',
    'gender': 'gender',
    'grade': 'grade',
    'Average_Reading_Score': 'Average Reading Score',
    'Average_Math_Score': 'Average Math Score',
    'School ID': 'School ID',
    'Total_Students': 'Total Students',
    'Total_Passing_Math': 'Total Passing Math',
    'Total_Passing_Reading': 'Total Passing Reading'
}, inplace=True)

merged['School Type'] = merged['School Type'].map({'District': 1, 'Charter': 2}).fillna(0).astype(int)
merged['student_name'] = merged['student_name'].astype(int)
merged['gender'] = merged['gender'].astype(int)
merged['grade'] = merged['grade'].astype(int)
merged['Average Reading Score'] = merged['Average Reading Score'].round().astype(int)
merged['Average Math Score'] = merged['Average Math Score'].round().astype(int)
merged['School ID'] = merged['School ID'].astype(int)
merged['size'] = merged['size'].astype(int)
merged['Total Budget'] = merged['Total Budget'].astype(int)
merged['Total Students'] = merged['Total Students'].astype(int)
merged['Total Passing Math'] = merged['Total Passing Math'].astype(int)
merged['Total Passing Reading'] = merged['Total Passing Reading'].astype(int)

merged = merged[['School Name', 'School Type', 'Total Students', 'student_name', 'gender', 'grade',
                 'Average Reading Score', 'Average Math Score', 'School ID', 'size', 'Total Budget',
                 'Total Passing Math', 'Total Passing Reading']]

merged.to_csv(output_path, index=False)