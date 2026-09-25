import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_38/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_38/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_38/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_38/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_38/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_38/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_38/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_38/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length1_38/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length1_38/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

result = df[['user_id', 'sad.depressed', 'open.stressed']].copy()
result.columns = ['user_id', 'sad', 'stressed']

result['user_id'] = result['user_id'].astype(int)
result['sad'] = result['sad'].astype(float)
result['stressed'] = result['stressed'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_38/target_multisource_mcts.csv", index=False)