import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_93/training_0.csv", index_col=0)

agg = df0.groupby('user_id').agg(
    time=('time', 'count'),
    bet=('bet', 'mean'),
    win=('win', 'mean')
).reset_index()

agg['time'] = agg['time'].astype(str)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_93/target_multisource_mcts.csv", index=False)