import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_1.csv", index_col=0)

# Join on school_name
merged = pd.merge(source1, source0[['school_name', 'type', 'size']], on='school_name', how='inner')

# Group by school_name and type, aggregate as required
agg = merged.groupby(['school_name', 'type']).agg(
    b=('Student ID', 'count'),
    c=('size', 'max'),
    d=('reading_score', 'mean'),
    e=('math_score', 'mean')
).reset_index()

# Rename columns to match target schema
result = agg.rename(columns={
    'type': 'a'
})[['school_name', 'a', 'b', 'c', 'd', 'e']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_68/target_multisource_mcts.csv", index=False)