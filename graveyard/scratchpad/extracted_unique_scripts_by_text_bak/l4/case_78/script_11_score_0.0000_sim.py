import pandas as pd
import numpy as np

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_2.csv", index_col=0)

# Step 1: From src2 (student scores), compute per school aggregates:
# Average Math Score, Average Reading Score, Number Passing Math, Number Passing Reading, School Size
# Passing means score >= 70 (typical passing threshold)
passing_math = src2['math_score'] >= 70
passing_reading = src2['reading_score'] >= 70

agg = src2.groupby('school').agg(
    **{
        'Average Math Score': ('math_score', 'mean'),
        'Average Reading Score': ('reading_score', 'mean'),
        'Number Passing Math': (passing_math.name, lambda x: passing_math[x.index].sum()),
        'Number Passing Reading': (passing_reading.name, lambda x: passing_reading[x.index].sum()),
        'School Size': ('Student ID', 'count')
    }
).reset_index()

# Step 2: Join src0 (which has school-level scores and passing counts) with agg on school to verify or replace
# But src0 has similar columns, so we can trust src0 for scores and passing counts, and src2 for School Size
# However, src0 does not have School Size, so we keep src0's scores and passing counts, and add School Size from agg

# Merge src0 and agg on 'school' to get School Size from agg
merged_scores = pd.merge(src0, agg[['school', 'School Size']], on='school', how='left')

# Step 3: Join merged_scores with src1 on school name to get School ID, type, size, budget
final = pd.merge(merged_scores, src1, left_on='school', right_on='name', how='inner')

# Step 4: Rename columns and reorder to match target schema
final = final.rename(columns={
    'school': 'name',
    'size': 'size',
    'budget': 'budget',
    'School ID': 'School ID',
    'type': 'type',
    'Average Math Score': 'Average Math Score',
    'Average Reading Score': 'Average Reading Score',
    'Number Passing Math': 'Number Passing Math',
    'Number Passing Reading': 'Number Passing Reading',
    'School Size': 'School Size'
})

final = final[['School ID', 'name', 'type', 'size', 'budget', 'Average Math Score', 'Average Reading Score',
               'Number Passing Math', 'Number Passing Reading', 'School Size']]

# Fix data types to match target schema
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

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_78/target_multisource_mcts.csv", index=False)