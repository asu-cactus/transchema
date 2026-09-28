import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_68/training_0.csv", index_col=0)
df['V_GENE'] = df['V_CALL'].str.split('-').str[0]
result = df.groupby('V_GENE', as_index=False).size().drop(columns='size', errors='ignore')
result = result[['V_GENE']]
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_68/target_multisource_mcts.csv", index=False)