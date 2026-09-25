import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_94/training_0.csv", index_col=0)

agg0 = pd.DataFrame()
agg0['0'] = (df0['0'] * df0['1']).sum()
agg0['1'] = (df0['2'] * df0['3']).sum()
agg0['2'] = 0.0
agg0['3'] = 0.0

agg0 = agg0.astype(float)

agg0.to_csv("autopipeline-benchmarks/github-pipelines/length2_94/target_multisource_mcts.csv", index=False)