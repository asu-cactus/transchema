import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_95/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_95/training_1.csv", index_col=0)

# Rename columns in df0 for clarity and to match target schema names
df0_renamed = df0.rename(columns={
    'name': 'School Name',
    'size': 'School Size',
    'budget': 'School Budget',
    'School ID': 'School ID'
})

# Join student data with school data on school name
merged = pd.merge(df1, df0_renamed[['School Name', 'School ID', 'School Size', 'School Budget']],
                  left_on='school', right_on='School Name', how='inner')

# Group by School Name, Student Grade, School ID
grouped = merged.groupby(['School Name', 'grade', 'School ID'], as_index=False).agg({
    'Student ID': 'count',               # count of students
    'reading_score': 'mean',             # average reading score
    'math_score': 'mean',                # average math score
    'School Size': 'first',              # same for all rows in group
    'School Budget': 'first'             # same for all rows in group
})

# Rename columns to match target schema
grouped = grouped.rename(columns={
    'grade': 'Student Grade',
    'Student ID': 'Student ID',
    'reading_score': 'Student Reading Score',
    'math_score': 'Average Student Math Score'
})

# Reorder columns to match target schema
grouped = grouped[['School Name', 'Student Grade', 'School ID', 'School Size', 'School Budget',
                   'Student ID', 'Student Reading Score', 'Average Student Math Score']]

# Cast columns to correct types
grouped['School Name'] = grouped['School Name'].astype(str)
grouped['Student Grade'] = grouped['Student Grade'].astype(str)
grouped['School ID'] = grouped['School ID'].astype('Int64')
grouped['School Size'] = grouped['School Size'].astype('Int64')
grouped['School Budget'] = grouped['School Budget'].astype('Int64')
grouped['Student ID'] = grouped['Student ID'].astype(float)
grouped['Student Reading Score'] = grouped['Student Reading Score'].astype(float)
grouped['Average Student Math Score'] = grouped['Average Student Math Score'].astype(float)

# Write output
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_95/target_multisource_mcts.csv", index=False)