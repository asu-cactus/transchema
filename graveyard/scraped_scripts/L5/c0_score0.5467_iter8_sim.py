import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_0/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_0/training_1.csv", index_col=0)

df0_renamed = df0.rename(columns={
    'school_name': 'School Name',
    'type': 'School Type',
    'size': 'size',
    'budget': 'Total Budget',
    'School ID': 'School ID'
})
df0_renamed['School Type'] = df0_renamed['School Type'].map({'District':1, 'Charter':2}).fillna(0).astype(int)

df1_renamed = df1.rename(columns={
    'school_name': 'School Name',
    'student_name': 'student_name',
    'gender': 'gender',
    'grade': 'grade',
    'reading_score': 'Average Reading Score',
    'math_score': 'Average Math Score'
})

df1_renamed['gender'] = df1_renamed['gender'].map({'F':1, 'M':0}).astype(int)
df1_renamed['grade'] = df1_renamed['grade'].str.extract('(\d+)').astype(int)

df0_renamed['Total Students'] = 0
df0_renamed['student_name'] = 0
df0_renamed['gender'] = 0
df0_renamed['grade'] = 0
df0_renamed['Average Reading Score'] = 0
df0_renamed['Average Math Score'] = 0
df0_renamed['Total Passing Math'] = 0
df0_renamed['Total Passing Reading'] = 0

df1_renamed['School Type'] = 0
df1_renamed['size'] = 0
df1_renamed['Total Budget'] = 0
df1_renamed['School ID'] = 0
df1_renamed['Total Students'] = 0
df1_renamed['Total Passing Math'] = 0
df1_renamed['Total Passing Reading'] = 0

union_df = pd.concat([df0_renamed, df1_renamed], ignore_index=True, sort=False)

pivot_df = union_df.pivot_table(
    index=['School Name', 'School Type', 'size', 'Total Budget', 'School ID'],
    values=['student_name', 'gender', 'grade', 'Average Reading Score', 'Average Math Score'],
    aggfunc={
        'student_name': 'count',
        'gender': 'mean',
        'grade': 'mean',
        'Average Reading Score': 'mean',
        'Average Math Score': 'mean'
    }
).reset_index()

pivot_df['student_name'] = pivot_df['student_name'].astype(int)
pivot_df['gender'] = pivot_df['gender'].round().astype(int)
pivot_df['grade'] = pivot_df['grade'].round().astype(int)
pivot_df['Average Reading Score'] = pivot_df['Average Reading Score'].round().astype(int)
pivot_df['Average Math Score'] = pivot_df['Average Math Score'].round().astype(int)

pivot_df['Total Students'] = pivot_df['student_name']

pivot_df['Total Passing Math'] = 0
pivot_df['Total Passing Reading'] = 0

cols = ['School Name', 'School Type', 'Total Students', 'student_name', 'gender', 'grade',
        'Average Reading Score', 'Average Math Score', 'School ID', 'size', 'Total Budget',
        'Total Passing Math', 'Total Passing Reading']

pivot_df = pivot_df[cols]

pivot_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_0/target_multisource_mcts.csv", index=False)