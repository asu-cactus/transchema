import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_1.csv", index_col=0)

agg_counts = source1.groupby(['school_name']).agg(
    b=('Student ID', 'count'),
    d=('reading_score', 'mean'),
    e=('math_score', 'mean')
).reset_index()

agg_size = source0[['school_name', 'type', 'size']]

merged = pd.merge(agg_counts, agg_size, on='school_name', how='inner')

result = merged.rename(columns={
    'school_name': 'school_name',
    'type': 'a',
    'b': 'b',
    'size': 'c',
    'd': 'd',
    'e': 'e'
})[['school_name', 'a', 'b', 'c', 'd', 'e']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_68/target_multisource_mcts.csv", index=False)