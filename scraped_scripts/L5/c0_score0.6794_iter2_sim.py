import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length5_0/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length5_0/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length5_0/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

df1['grade'] = df1['grade'].str.extract('(\d+)').astype(int)
df1['gender'] = df1['gender'].map({'F': 1, 'M': 0})

agg = df1.groupby(['school_name', 'gender', 'grade']).agg(
    Total_Students=('student_name', 'count'),
    Average_Reading_Score=('reading_score', 'mean'),
    Average_Math_Score=('math_score', 'mean')
).reset_index()

merged = pd.merge(df0, agg, how='inner', left_on='school_name', right_on='school_name')

merged['School Name'] = merged['school_name']
merged['School Type'] = merged['type'].map({'District': 1, 'Charter': 2}).fillna(0).astype(int)
merged['Total Students'] = merged['Total_Students'].astype(int)
merged['student_name'] = 1
merged['gender'] = merged['gender'].astype(int)
merged['grade'] = merged['grade'].astype(int)
merged['Average Reading Score'] = merged['Average_Reading_Score'].round().astype(int)
merged['Average Math Score'] = merged['Average_Math_Score'].round().astype(int)
merged['School ID'] = merged['School ID'].astype(int)
merged['size'] = merged['size'].astype(int)
merged['Total Budget'] = merged['budget'].astype(int)
merged['Total Passing Math'] = 0
merged['Total Passing Reading'] = 0

result = merged[['School Name', 'School Type', 'Total Students', 'student_name', 'gender', 'grade',
                 'Average Reading Score', 'Average Math Score', 'School ID', 'size', 'Total Budget',
                 'Total Passing Math', 'Total Passing Reading']]

result.to_csv(target_path, index=False)