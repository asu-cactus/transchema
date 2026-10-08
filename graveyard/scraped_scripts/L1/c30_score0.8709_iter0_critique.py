import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_30/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_30/training_1.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length1_30/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Join Source0 and Source1 on movieId
result = pd.merge(df0, df1, on='movieId', how='inner')

# Reorder columns to match target schema
result = result[['movieId', 'title', 'genres', 'userId', 'tag', 'timestamp']]

# Cast columns to correct types
result = result.astype({
    'movieId': 'int64',
    'title': 'string',
    'genres': 'string',
    'userId': 'int64',
    'tag': 'string',
    'timestamp': 'int64'
})

result.to_csv(output_path, index=False)