import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_87/training_0.csv", index_col=0)

# Extract last name by splitting on comma and taking the first part, then strip whitespace
result = source0['Name'].dropna().map(lambda x: x.split(',')[0].strip())

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_87/target_multisource_mcts.csv", index=False, header=['Name'])