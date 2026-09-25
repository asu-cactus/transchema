import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_16/training_0.csv", index_col=0)

df = df.dropna(subset=['CUSTOMERNAME', 'ORDERNUMBER'])

df['ORDERNUMBER'] = df['ORDERNUMBER'].astype(str).str.strip()
df = df[df['ORDERNUMBER'].str.match(r'^\d+$')]
df['ORDERNUMBER'] = df['ORDERNUMBER'].astype(int)

agg_df = df.groupby(['CUSTOMERNAME', 'ORDERNUMBER'], dropna=False).agg({
    'QUANTITYORDERED': 'sum',
    'SALES': 'sum',
    'PRICEEACH': 'mean'
}).reset_index()

agg_df['ORDERNUMBER'] = agg_df['ORDERNUMBER'].astype(int)
result = agg_df[['CUSTOMERNAME', 'ORDERNUMBER']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_16/target_multisource_mcts.csv", index=False)