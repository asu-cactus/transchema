import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_41/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_41/training_1.csv", index_col=0)

merged = pd.merge(source0, source1, on='school_name', how='inner')

agg = merged.groupby('School ID').agg(
    **{
        'Total Students': ('Student ID', 'count'),
        'Total School Budget': ('budget', 'sum'),
        'Average Math Score': ('math_score', 'mean'),
        'Average Reading Score': ('reading_score', 'mean')
    }
).reset_index(drop=True)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_41/target_multisource_mcts.csv", index=False)