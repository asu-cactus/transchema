import pandas as pd

# Read sources
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_2.csv", index_col=0)

# Step 1: Aggregate student data (src2) by school
passing_math = src2['math_score'] >= 70
passing_reading = src2['reading_score'] >= 70

agg_student = src2.groupby('school').agg(
    **{
        'School Size': ('Student ID', 'count')
    }
).reset_index()

# Step 2: Merge src0 with agg_student on 'school' to add School Size
merged_scores = pd.merge(src0, agg_student, on='school', how='inner')

# Step 3: Join merged_scores with src1 on school name = name
merged_all = pd.merge(merged_scores, src1, left_on='school', right_on='name', how='inner')

# Step 4: Group by School ID and name to ensure uniqueness and aggregate other columns by first (since they should be unique per school)
grouped = merged_all.groupby(['School ID', 'name'], as_index=False).agg({
    'type': 'first',
    'size': 'first',
    'budget': 'first',
    'Average Math Score': 'first',
    'Average Reading Score': 'first',
    'Number Passing Math': 'first',
    'Number Passing Reading': 'first',
    'School Size': 'first'
})

# Step 5: Reorder columns to match target schema
final = grouped[['School ID', 'name', 'type', 'size', 'budget', 'Average Math Score', 'Average Reading Score',
                 'Number Passing Math', 'Number Passing Reading', 'School Size']]

# Step 6: Fix data types to match target schema
final['School ID'] = final['School ID'].astype(int)
final['name'] = final['name'].astype(str)
final['type'] = final['type'].astype(str)
final['size'] = final['size'].astype(int)
final['budget'] = final['budget'].astype(int)
final['Average Math Score'] = final['Average Math Score'].astype(float)
final['Average Reading Score'] = final['Average Reading Score'].astype(float)
final['Number Passing Math'] = final['Number Passing Math'].astype(int)
final['Number Passing Reading'] = final['Number Passing Reading'].astype(int)
final['School Size'] = final['School Size'].astype(int)

# Write output
final.to_csv("autopipeline-benchmarks/github-pipelines/length4_78/target_multisource_mcts.csv", index=False)