import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

pivot_df = df_all.pivot_table(index='zipcode', columns='businesses', values='counts', fill_value=0)

pivot_df = pivot_df.rename(columns={
    'Sidewalk Cafe': 'businesses_x',
    'Pawnbroker': 'businesses_y',
    'Debt Collection Agency': 'businesses_x_5',
    'Cigarette Retail Dealer': 'businesses_y_7'
})

pivot_df = pivot_df.rename(columns={
    'businesses_x': 'counts_x',
    'businesses_y': 'counts_y',
    'businesses_x_5': 'counts_x_6',
    'businesses_y_7': 'counts_y_8'
})

pivot_df = pivot_df.reset_index()

pivot_df.to_csv("autopipeline-benchmarks/github-pipelines/length3_52/target_multisource_mcts.csv", index=False)