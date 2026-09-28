import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length3_12/training_0.csv"

df0 = pd.read_csv(source0_path, index_col=0)

df_joined = pd.merge(df0, df0, on="Item ID", suffixes=('_left', '_right'))

grouped = df_joined.groupby('SN_left').agg(
    Price=('Price_left', 'first'),
    count=('Item ID', 'count')
).reset_index()

grouped.rename(columns={'SN_left': 'SN'}, inplace=True)

grouped['Price'] = grouped['Price'].astype(float)
grouped['count'] = grouped['count'].astype(int)
grouped['SN'] = grouped['SN'].astype(str)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_12/target_multisource_mcts.csv", index=False)