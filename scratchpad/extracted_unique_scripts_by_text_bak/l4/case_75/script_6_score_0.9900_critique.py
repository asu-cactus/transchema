import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_75/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_75/training_1.csv", index_col=0)

# Join Source1 and Source0 on school_name
merged = pd.merge(source1, source0[['school_name', 'type']], on='school_name', how='inner')

# Group by 'type' and aggregate average reading_score and math_score
result = merged.groupby('type')[['reading_score', 'math_score']].mean().reset_index()

# Rename columns to match target schema
result = result.rename(columns={'reading_score': 'a', 'math_score': 'b'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_75/target_multisource_mcts.csv", index=False)