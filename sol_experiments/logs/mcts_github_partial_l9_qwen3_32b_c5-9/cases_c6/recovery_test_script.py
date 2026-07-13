import pandas as pd

sources = []
base_path = "autopipeline-benchmarks/github-pipelines/length9_6/training_"
for i in range(17):
    path = f"{base_path}{i}.csv"
    df = pd.read_csv(path, index_col=0)
    sources.append(df)

result = pd.concat(sources, ignore_index=True)
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_6/target_multisource_mcts_recovery_test_val.csv")