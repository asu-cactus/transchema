import pandas as pd
import numpy as np

source0_path = "autopipeline-benchmarks/github-pipelines/length5_0/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length5_0/training_1.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length5_0/target_multisource_mcts.csv"

# Read sources
df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Preprocess source1
df1['grade'] = df1['grade'].str.extract('(\d+)').astype(int)
df1['gender'] = df1['gender'].map({'F': 1, 'M': 0}).fillna(0).astype(int)

# Map 'type' in df0 to integer for 'School Type'
df0['School Type'] = df0['type'].map({'District': 1, 'Charter': 2}).fillna(0).astype(int)

# Join on 'school_name'
merged = pd.merge(df0, df1, left_on='school_name', right_on='school_name', how='inner')

# Group by 'school_name' and 'School ID' (from df0)
grouped = merged.groupby(['school_name', 'School ID'], as_index=False).agg(
    # 'School Type' is unique per school, take first
    School_Type=('School Type', 'first'),
    # Total Students: count of student_name
    Total_Students=('student_name', 'count'),
    # student_name: same as Total Students (count)
    student_name=('student_name', 'count'),
    # gender: sum of gender (number of females)
    gender=('gender', 'sum'),
    # grade: mean rounded
    grade=('grade', lambda x: int(round(x.mean()))),
    # Average Reading Score: mean rounded
    Average_Reading_Score=('reading_score', lambda x: int(round(x.mean()))),
    # Average Math Score: mean rounded
    Average_Math_Score=('math_score', lambda x: int(round(x.mean()))),
    # size: unique per school, take first
    size=('size', 'first'),
    # Total Budget: unique per school, take first
    Total_Budget=('budget', 'first'),
    # Total Passing Math: count of math_score >= 70
    Total_Passing_Math=('math_score', lambda x: (x >= 70).sum()),
    # Total Passing Reading: count of reading_score >= 70
    Total_Passing_Reading=('reading_score', lambda x: (x >= 70).sum())
)

# Rename columns to match target schema exactly
grouped.rename(columns={
    'school_name': 'School Name',
    'School_Type': 'School Type',
    'Total_Students': 'Total Students',
    'student_name': 'student_name',
    'gender': 'gender',
    'grade': 'grade',
    'Average_Reading_Score': 'Average Reading Score',
    'Average_Math_Score': 'Average Math Score',
    'size': 'size',
    'Total_Budget': 'Total Budget',
    'Total_Passing_Math': 'Total Passing Math',
    'Total_Passing_Reading': 'Total Passing Reading'
}, inplace=True)

# Ensure correct types
grouped['School Type'] = grouped['School Type'].astype(int)
grouped['Total Students'] = grouped['Total Students'].astype(int)
grouped['student_name'] = grouped['student_name'].astype(int)
grouped['gender'] = grouped['gender'].astype(int)
grouped['grade'] = grouped['grade'].astype(int)
grouped['Average Reading Score'] = grouped['Average Reading Score'].astype(int)
grouped['Average Math Score'] = grouped['Average Math Score'].astype(int)
grouped['School ID'] = grouped['School ID'].astype(int)
grouped['size'] = grouped['size'].astype(int)
grouped['Total Budget'] = grouped['Total Budget'].astype(int)
grouped['Total Passing Math'] = grouped['Total Passing Math'].astype(int)
grouped['Total Passing Reading'] = grouped['Total Passing Reading'].astype(int)

# Reorder columns to match target schema
grouped = grouped[['School Name', 'School Type', 'Total Students', 'student_name', 'gender', 'grade',
                   'Average Reading Score', 'Average Math Score', 'School ID', 'size', 'Total Budget',
                   'Total Passing Math', 'Total Passing Reading']]

# Write output
grouped.to_csv(output_path, index=False)