import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_95/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_95/training_1.csv", index_col=0)

joined = pd.merge(df0, df1, left_on="name", right_on="school", how="inner")

agg = joined.groupby(
    ['name', 'grade', 'School ID', 'size', 'budget', 'Student ID'],
    as_index=False
).agg({
    'reading_score': 'mean',
    'math_score': 'mean'
})

agg = agg.rename(columns={
    'name': 'School Name',
    'grade': 'Student Grade',
    'size': 'School Size',
    'budget': 'School Budget',
    'reading_score': 'Student Reading Score',
    'math_score': 'Average Student Math Score',
    'Student ID': 'Student ID',
    'School ID': 'School ID'
})

agg['School ID'] = agg['School ID'].astype(int)
agg['School Size'] = agg['School Size'].astype(int)
agg['School Budget'] = agg['School Budget'].astype(int)
agg['Student ID'] = agg['Student ID'].astype(float)
agg['Student Grade'] = agg['Student Grade'].astype(str)
agg['School Name'] = agg['School Name'].astype(str)
agg['Student Reading Score'] = agg['Student Reading Score'].astype(float)
agg['Average Student Math Score'] = agg['Average Student Math Score'].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length2_95/target_multisource_mcts.csv", index=False)