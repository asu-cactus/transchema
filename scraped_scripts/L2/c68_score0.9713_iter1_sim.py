import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_68/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_68/training_1.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length2_68/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

pivot = df1.pivot_table(index='school_name', columns='grade', values=['math_score', 'reading_score'], aggfunc='mean')
pivot.columns = [f"{val} {col}" for val, col in pivot.columns]
pivot = pivot.reset_index()

merged = pd.merge(pivot, df0, on='school_name', how='inner')

agg = merged.groupby(['school_name', 'type'], as_index=False).agg({
    'size': 'sum',
    'budget': 'sum',
    'math_score 9th': 'mean',
    'math_score 10th': 'mean',
    'math_score 11th': 'mean',
    'math_score 12th': 'mean',
    'reading_score 9th': 'mean',
    'reading_score 10th': 'mean',
    'reading_score 11th': 'mean',
    'reading_score 12th': 'mean'
})

agg['Total Students'] = agg['size']
agg['Total School Budget'] = agg['budget']

math_cols = ['math_score 9th', 'math_score 10th', 'math_score 11th', 'math_score 12th']
reading_cols = ['reading_score 9th', 'reading_score 10th', 'reading_score 11th', 'reading_score 12th']

agg['Average Math Score'] = agg[math_cols].mean(axis=1)
agg['Average Reading Score'] = agg[reading_cols].mean(axis=1)

result = agg[['school_name', 'type', 'Total Students', 'Total School Budget', 'Average Math Score', 'Average Reading Score']]

result['Total Students'] = result['Total Students'].astype(int)
result['Total School Budget'] = result['Total School Budget'].astype(int)
result['Average Math Score'] = result['Average Math Score'].astype(float)
result['Average Reading Score'] = result['Average Reading Score'].astype(float)

result.to_csv(output_path, index=False)