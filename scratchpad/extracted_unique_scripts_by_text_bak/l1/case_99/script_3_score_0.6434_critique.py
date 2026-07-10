import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_99/training_0.csv", index_col=0)

df = df0.astype({
    'user_id': 'int64',
    'timestamp': 'string',
    'source': 'string',
    'device': 'string',
    'operative_system': 'string',
    'test': 'int64',
    'price': 'int64',
    'converted': 'int64'
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_99/target_multisource_mcts.csv", index=False)