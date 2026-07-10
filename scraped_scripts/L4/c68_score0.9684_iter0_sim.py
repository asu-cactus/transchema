import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_1.csv", index_col=0)

agg_source0 = source0.groupby('school_name').agg({
    'type': 'first',
    'size': 'sum',
    'budget': 'sum'
}).reset_index()

agg_source1 = source1.groupby('school_name').agg({
    'reading_score': 'mean',
    'math_score': 'mean'
}).reset_index()

merged = pd.merge(agg_source0, agg_source1, on='school_name', how='inner')

merged = merged.rename(columns={
    'type': 'a',
    'size': 'b',
    'budget': 'c',
    'reading_score': 'd',
    'math_score': 'e'
})

merged['b'] = merged['b'].astype(int)
merged['c'] = merged['c'].astype(int)
merged['d'] = merged['d'].astype(float)
merged['e'] = merged['e'].astype(float)

merged.to_csv("autopipeline-benchmarks/github-pipelines/length4_68/target_multisource_mcts.csv", index=False)