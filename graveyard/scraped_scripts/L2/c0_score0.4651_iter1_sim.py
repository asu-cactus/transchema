import pandas as pd

source1_path = "autopipeline-benchmarks/github-pipelines/length2_0/training_1.csv"

df1 = pd.read_csv(source1_path, index_col=0)

result = pd.concat([df1, df1], ignore_index=True)[['school_name', 'reading_score']]
result['reading_score'] = result['reading_score'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_0/target_multisource_mcts.csv", index=False)