import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_77/training_0.csv", index_col=0)

result = df0[['fac_type', 'capacity']].copy()
result['fac_type'] = result['fac_type'].astype(str)
result['capacity'] = pd.to_numeric(result['capacity'], errors='coerce').fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_77/target_multisource_mcts.csv", index=False)