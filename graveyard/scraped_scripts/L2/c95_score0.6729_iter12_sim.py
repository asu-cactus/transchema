import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_95/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_95/training_1.csv", index_col=0)

agg = df1.groupby(['gender', 'grade', 'school']).agg(
    Student_ID=('Student ID', 'count'),
    Student_Reading_Score=('reading_score', 'mean'),
    Average_Student_Math_Score=('math_score', 'mean')
).reset_index()

df0_filtered = df0[df0['type'].notna()]

agg_full = agg.merge(df0_filtered, left_on='school', right_on='name', how='inner')

agg_full = agg_full.groupby(['type', 'gender', 'grade', 'school', 'School ID', 'name', 'size', 'budget'], as_index=False).agg({
    'Student_ID': 'sum',
    'Student_Reading_Score': 'mean',
    'Average_Student_Math_Score': 'mean'
})

agg_full.rename(columns={
    'name': 'School Name',
    'grade': 'Student Grade',
    'School ID': 'School ID',
    'size': 'School Size',
    'budget': 'School Budget',
    'Student_ID': 'Student ID',
    'Student_Reading_Score': 'Student Reading Score',
    'Average_Student_Math_Score': 'Average Student Math Score'
}, inplace=True)

agg_full = agg_full[['School Name', 'Student Grade', 'School ID', 'School Size', 'School Budget', 'Student ID', 'Student Reading Score', 'Average Student Math Score']]

agg_full['School ID'] = agg_full['School ID'].astype('int64')
agg_full['School Size'] = agg_full['School Size'].astype('int64')
agg_full['School Budget'] = agg_full['School Budget'].astype('int64')
agg_full['Student ID'] = agg_full['Student ID'].astype('float64')
agg_full['Student Reading Score'] = agg_full['Student Reading Score'].astype('float64')
agg_full['Average Student Math Score'] = agg_full['Average Student Math Score'].astype('float64')
agg_full['Student Grade'] = agg_full['Student Grade'].astype(str)
agg_full['School Name'] = agg_full['School Name'].astype(str)

agg_full.to_csv("autopipeline-benchmarks/github-pipelines/length2_95/target_multisource_mcts.csv", index=False)