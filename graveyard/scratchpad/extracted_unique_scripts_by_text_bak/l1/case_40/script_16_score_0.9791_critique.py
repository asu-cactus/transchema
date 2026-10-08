import pandas as pd
import glob

file_paths = glob.glob("autopipeline-benchmarks/github-pipelines/length1_40/training_*.csv")

df_list = [pd.read_csv(fp, index_col=0) for fp in file_paths]
df = pd.concat(df_list, ignore_index=True)

df_grouped = df.groupby(['CUSTOMERNAME', 'ORDERNUMBER'], as_index=False)['QUANTITYORDERED'].sum()

df_grouped['ORDERNUMBER'] = df_grouped['ORDERNUMBER'].astype(int)
df_grouped['QUANTITYORDERED'] = df_grouped['QUANTITYORDERED'].astype(int)
df_grouped['CUSTOMERNAME'] = df_grouped['CUSTOMERNAME'].astype(str)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_40/target_multisource_mcts.csv", index=False)