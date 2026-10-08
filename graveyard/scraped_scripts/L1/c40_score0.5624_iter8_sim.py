import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_40/training_0.csv", index_col=0)
df = df[df['CUSTOMERNAME'].notnull() & df['ORDERNUMBER'].notnull() & df['QUANTITYORDERED'].notnull()]
df = df[['CUSTOMERNAME', 'ORDERNUMBER', 'QUANTITYORDERED']]
df['ORDERNUMBER'] = df['ORDERNUMBER'].astype(int)
df['QUANTITYORDERED'] = df['QUANTITYORDERED'].astype(int)
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_40/target_multisource_mcts.csv", index=False)