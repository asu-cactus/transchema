import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_22/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_22/training_1.csv", index_col=0)

df1_subset = df1[['school_name', 'math_score']]

df_union = pd.concat([df0[['school_name']].assign(math_score=0), df1_subset], ignore_index=True)

result = df_union.groupby('school_name', as_index=False)['math_score'].sum()

result['math_score'] = result['math_score'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_22/target_multisource_mcts.csv", index=False)