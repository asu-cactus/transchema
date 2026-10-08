import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_1.csv", index_col=0)

# Join on school_name
joined = pd.merge(source0, source1, on='school_name', how='inner')

# Group by school_name and type, aggregate size and budget by sum, reading_score and math_score by mean
agg = joined.groupby(['school_name', 'type'], as_index=False).agg({
    'size': 'sum',
    'budget': 'sum',
    'reading_score': 'mean',
    'math_score': 'mean'
})

# Rename columns to match target schema
result = pd.DataFrame()
result['school_name'] = agg['school_name']
result['a'] = agg['type']
result['b'] = agg['size'].astype(int)
result['c'] = agg['budget'].astype(int)
result['d'] = agg['reading_score'].astype(float)
result['e'] = agg['math_score'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_68/target_multisource_mcts.csv", index=False)