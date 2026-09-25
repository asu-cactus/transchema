import pandas as pd

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_7/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_7/training_1.csv", index_col=0)

df = pd.concat([df1, df2], ignore_index=True)

result = df[['contributor_firstname', 'contributor_lastname', 'amount']].copy()
result['contributor_firstname'] = result['contributor_firstname'].astype(str)
result['contributor_lastname'] = result['contributor_lastname'].astype(str)
result['amount'] = result['amount'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_7/target_multisource_mcts.csv", index=False)