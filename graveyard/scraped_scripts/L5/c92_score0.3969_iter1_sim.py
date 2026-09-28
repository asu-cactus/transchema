import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_92/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_92/training_0.csv", index_col=0)

df_union = pd.concat([df0, df1], ignore_index=True)

df_union = df_union.rename(columns={
    'NY.GDP.MKTP.KN': 'NY.GDP.MKTP.KN_x',
    'SI.DST.10TH.10': 'SI.DST.10TH.10_x',
    'SP.POP.TOTL': 'SP.POP.TOTL_x'
})

df_union['NY.GDP.MKTP.KN_y'] = df_union['NY.GDP.MKTP.KN_x']
df_union['SI.DST.10TH.10_y'] = df_union['SI.DST.10TH.10_x']
df_union['SP.POP.TOTL_y'] = df_union['SP.POP.TOTL_x']

df_union['NY.GDP.MKTP.KN'] = df_union['NY.GDP.MKTP.KN_x']
df_union['SI.DST.10TH.10'] = df_union['SI.DST.10TH.10_x']
df_union['SP.POP.TOTL'] = df_union['SP.POP.TOTL_x']

df_union = df_union[['country',
                     'NY.GDP.MKTP.KN_x', 'SI.DST.10TH.10_x', 'SP.POP.TOTL_x',
                     'NY.GDP.MKTP.KN_y', 'SI.DST.10TH.10_y', 'SP.POP.TOTL_y',
                     'NY.GDP.MKTP.KN', 'SI.DST.10TH.10', 'SP.POP.TOTL']]

df_union.to_csv("autopipeline-benchmarks/github-pipelines/length5_92/target_multisource_mcts.csv", index=False)