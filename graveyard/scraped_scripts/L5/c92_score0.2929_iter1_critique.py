import pandas as pd

# Read the single source table three times (aliases)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_92/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_92/training_0.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_92/training_0.csv", index_col=0)

# First join df0 and df1 on 'country'
df_join1 = pd.merge(df0, df1, on='country', suffixes=('_x', '_y'))

# Then join the result with df2 on 'country'
df_final = pd.merge(df_join1, df2, on='country')

# Rename columns of df2 (no suffix) to match target schema (no suffix)
# Columns from df2 are already without suffix, so no rename needed

# Select columns exactly as in target schema:
# ['country', 
#  'NY.GDP.MKTP.KN_x', 'SI.DST.10TH.10_x', 'SP.POP.TOTL_x',
#  'NY.GDP.MKTP.KN_y', 'SI.DST.10TH.10_y', 'SP.POP.TOTL_y',
#  'NY.GDP.MKTP.KN', 'SI.DST.10TH.10', 'SP.POP.TOTL']

df_final = df_final[['country',
                     'NY.GDP.MKTP.KN_x', 'SI.DST.10TH.10_x', 'SP.POP.TOTL_x',
                     'NY.GDP.MKTP.KN_y', 'SI.DST.10TH.10_y', 'SP.POP.TOTL_y',
                     'NY.GDP.MKTP.KN', 'SI.DST.10TH.10', 'SP.POP.TOTL']]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length5_92/target_multisource_mcts.csv", index=False)