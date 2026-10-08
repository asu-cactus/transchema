import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_22/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on="condition", suffixes=('_left', '_right'))

pivoted = joined.pivot_table(index='condition', values=['click_left', 'click_right'], aggfunc='sum').reset_index()

pivoted['click'] = pivoted['click_left'] + pivoted['click_right']

result = pivoted[['condition', 'click']].astype({'condition': int, 'click': int})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_22/target_multisource_mcts.csv", index=False)