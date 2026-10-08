import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_16/training_0.csv", index_col=0)

agg_df = df0.groupby(['CUSTOMERNAME', 'ORDERNUMBER'], as_index=False).agg({
    'QUANTITYORDERED': 'sum',
    'SALES': 'sum',
    'PRICEEACH': 'mean'
})

agg_df['ORDERNUMBER'] = agg_df['ORDERNUMBER'].astype(int)
agg_df['CUSTOMERNAME'] = agg_df['CUSTOMERNAME'].astype(str)

result = agg_df[['CUSTOMERNAME', 'ORDERNUMBER']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_16/target_multisource_mcts.csv", index=False)