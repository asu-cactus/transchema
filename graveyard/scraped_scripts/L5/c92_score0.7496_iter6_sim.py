import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_92/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, on="country", suffixes=('_x', '_y'))

agg_dict = {
    'NY.GDP.MKTP.KN_x': 'mean',
    'SI.DST.10TH.10_x': 'mean',
    'SP.POP.TOTL_x': 'mean',
    'NY.GDP.MKTP.KN_y': 'mean',
    'SI.DST.10TH.10_y': 'mean',
    'SP.POP.TOTL_y': 'mean',
    'NY.GDP.MKTP.KN': 'mean',
    'SI.DST.10TH.10': 'mean',
    'SP.POP.TOTL': 'mean'
}

df_joined['NY.GDP.MKTP.KN'] = df_joined['NY.GDP.MKTP.KN_x']
df_joined['SI.DST.10TH.10'] = df_joined['SI.DST.10TH.10_x']
df_joined['SP.POP.TOTL'] = df_joined['SP.POP.TOTL_x']

grouped = df_joined.groupby('country', as_index=False).agg({
    'NY.GDP.MKTP.KN_x': 'mean',
    'SI.DST.10TH.10_x': 'mean',
    'SP.POP.TOTL_x': 'mean',
    'NY.GDP.MKTP.KN_y': 'mean',
    'SI.DST.10TH.10_y': 'mean',
    'SP.POP.TOTL_y': 'mean',
    'NY.GDP.MKTP.KN': 'mean',
    'SI.DST.10TH.10': 'mean',
    'SP.POP.TOTL': 'mean'
})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_92/target_multisource_mcts.csv", index=False)