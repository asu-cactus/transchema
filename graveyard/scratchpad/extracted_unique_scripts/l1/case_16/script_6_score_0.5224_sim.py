import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_16/training_0.csv", index_col=0)
df0_filtered = df0[df0['CUSTOMERNAME'].notnull() & df0['ORDERNUMBER'].notnull()]
df0_projected = df0_filtered[['CUSTOMERNAME', 'ORDERNUMBER']].copy()
df0_projected['CUSTOMERNAME'] = df0_projected['CUSTOMERNAME'].astype(str)
df0_projected['ORDERNUMBER'] = df0_projected['ORDERNUMBER'].astype(int)
df0_projected.to_csv("autopipeline-benchmarks/github-pipelines/length1_16/target_multisource_mcts.csv", index=False)