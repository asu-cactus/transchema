import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_42/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_42/training_1.csv", index_col=0)

pivot = source1.pivot_table(index='school_name', columns='grade', values=['math_score', 'reading_score'], aggfunc='mean')
pivot.columns = [f"{val}_{col}" for val, col in pivot.columns]
pivot.reset_index(inplace=True)

merged = pd.merge(pivot, source0, on='school_name', how='inner')

agg = merged.groupby('size').agg({
    'size': 'sum',
    'budget': 'sum',
    'math_score_9th': 'mean',
    'reading_score_9th': 'mean'
}).rename(columns={
    'size': 'School Size',
    'budget': 'Total School Budget',
    'math_score_9th': 'Average Math Score',
    'reading_score_9th': 'Average Reading Score'
})

agg['Total Students'] = agg['School Size']

agg = agg[['School Size', 'Total Students', 'Total School Budget', 'Average Math Score', 'Average Reading Score']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_42/target_multisource_mcts.csv")