import pandas as pd

source_path = "autopipeline-benchmarks/github-pipelines/length1_93/training_0.csv"
df = pd.read_csv(source_path, index_col=0)

# Ensure correct dtypes matching target schema
df = df.astype({
    'user_id': 'string',
    'time': 'string',
    'bet': 'float',
    'win': 'float'
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_93/target_multisource_mcts.csv", index=False)