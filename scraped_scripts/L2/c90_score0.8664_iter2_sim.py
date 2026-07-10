import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_90/training_0.csv", index_col=0)

agg = df0.groupby(['day', 'metric']).agg(
    count_value=('value', 'count'),
    avg_value=('value', 'mean'),
    max_value=('value', 'max')
).reset_index()

agg['value'] = agg['count_value'] + agg['avg_value'] + agg['max_value']

result = agg[['day', 'metric', 'value']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_90/target_multisource_mcts.csv", index=False)