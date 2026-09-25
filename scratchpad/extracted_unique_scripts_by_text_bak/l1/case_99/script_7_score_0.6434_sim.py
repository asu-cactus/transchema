import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_99/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, left_on='source', right_on='source', suffixes=('', '_dup'))

grouped = joined.groupby('user_id', as_index=False).first()

result = grouped[['user_id', 'timestamp', 'source', 'device', 'operative_system', 'test', 'price', 'converted']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_99/target_multisource_mcts.csv", index=False)