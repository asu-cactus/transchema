import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_90/training_0.csv", index_col=0)

result = pd.concat([df0], ignore_index=True)

result['day'] = result['day'].astype(str)
result['metric'] = result['metric'].astype(str)
result['value'] = result['value'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_90/target_multisource_mcts.csv", index=False)