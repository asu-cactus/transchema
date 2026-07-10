import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_52/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

# Group by 'condition' and count number of rows where click == 0
result = df.groupby('condition', as_index=False).agg({'click': lambda x: (x == 0).sum()})

# Rename 'click' column to '0' as per target schema
result = result.rename(columns={'click': '0'})

# Ensure types match target schema
result['condition'] = result['condition'].astype(int)
result['0'] = result['0'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_52/target_multisource_mcts.csv", index=False)