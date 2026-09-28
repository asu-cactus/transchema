import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_1.csv", index_col=0)

df0_sub = df0[['Publisher']].copy()
df0_sub['Publisher'] = df0_sub['Publisher'].astype(str).str.strip()

df1_sub = df1[['hero_names']].copy()
df1_sub.rename(columns={'hero_names': 'Publisher'}, inplace=True)
df1_sub['Publisher'] = df1_sub['Publisher'].astype(str).str.strip()

result = pd.concat([df0_sub, df1_sub], ignore_index=True)

result['Publisher'] = result['Publisher'].astype('category').cat.codes + 1

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)