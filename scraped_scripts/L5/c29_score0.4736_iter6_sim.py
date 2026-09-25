import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_29/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_29/training_0.csv", index_col=0)

df_union = pd.concat([df0, df1], ignore_index=True)
result = df_union[['school_name', 'math_score']].copy()
result['school_name'] = result['school_name'].astype(str)
result['math_score'] = pd.to_numeric(result['math_score'], errors='coerce')

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_29/target_multisource_mcts.csv", index=False)