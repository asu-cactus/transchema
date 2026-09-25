import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_99/training_0.csv", index_col=0)

# Since only one source table is given, no join or group by is needed.
# Just output the source table as is, with columns in target schema order.

result = df0[['user_id', 'timestamp', 'source', 'device', 'operative_system', 'test', 'price', 'converted']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_99/target_multisource_mcts.csv", index=False)