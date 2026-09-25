import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_40/training_0.csv", index_col=0)
df_out = df[['CUSTOMERNAME', 'ORDERNUMBER', 'QUANTITYORDERED']].copy()
df_out['ORDERNUMBER'] = pd.to_numeric(df_out['ORDERNUMBER'], errors='coerce').astype('Int64')
df_out['QUANTITYORDERED'] = pd.to_numeric(df_out['QUANTITYORDERED'], errors='coerce').astype('Int64')
df_out.to_csv("autopipeline-benchmarks/github-pipelines/length1_40/target_multisource_mcts.csv", index=False)