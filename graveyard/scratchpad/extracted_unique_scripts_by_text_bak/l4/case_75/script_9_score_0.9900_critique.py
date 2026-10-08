import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_75/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_75/training_1.csv", index_col=0)

# Join source1 with source0 on school_name to get 'type'
merged = pd.merge(source1, source0[['school_name', 'type']], on='school_name', how='inner')

# Group by 'type' and aggregate average reading_score and math_score
agg = merged.groupby('type', as_index=False).agg({'reading_score': 'mean', 'math_score': 'mean'})

# Rename columns to match target schema
agg = agg.rename(columns={'reading_score': 'a', 'math_score': 'b'})

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_75/target_multisource_mcts.csv", index=False)