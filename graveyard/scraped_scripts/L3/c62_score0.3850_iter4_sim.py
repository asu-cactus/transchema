import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_62/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_62/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_62/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_62/training_3.csv", index_col=0)

df = df0.merge(df1, on="Wrestler", suffixes=('_2013', '_2014'))
df = df.merge(df2, on="Wrestler")
df = df.merge(df3, on="Wrestler", suffixes=('_2015', '_2016'))

df.rename(columns={
    'Wins_2013': '2013 Wins', 'Losses_2013': '2013 Losses', 'Draws_2013': '2013 Draws',
    'Wins_2014': '2014 Wins', 'Losses_2014': '2014 Losses', 'Draws_2014': '2014 Draws',
    'Wins': '2015 Wins', 'Losses': '2015 Losses', 'Draws': '2015 Draws',
    'Wins_2016': '2016 Wins', 'Losses_2016': '2016 Losses', 'Draws_2016': '2016 Draws'
}, inplace=True)

df.rename(columns={
    'Wins': '2015 Wins', 'Losses': '2015 Losses', 'Draws': '2015 Draws'
}, inplace=True)

# After merge with df2 (no suffix), columns from df2 are Wins, Losses, Draws (2015)
# After merge with df3 with suffixes _2015 and _2016, columns from df3 are suffixed _2016
# But suffixes=('_2015', '_2016') applies only to the last merge, so columns from df3 get _2016 suffix
# Columns from df2 remain without suffix, so rename them to 2015 columns

df.rename(columns={
    'Wins': '2015 Wins', 'Losses': '2015 Losses', 'Draws': '2015 Draws'
}, inplace=True)

# The last merge added _2016 suffix to df3 columns, so rename them accordingly
df.rename(columns={
    'Wins_2016': '2016 Wins', 'Losses_2016': '2016 Losses', 'Draws_2016': '2016 Draws'
}, inplace=True)

# But the last merge columns are actually 'Wins_2015' and 'Wins_2016' after suffixes, so let's check actual columns
# To avoid confusion, let's rename columns explicitly after each merge

# Let's redo merges with explicit suffixes to avoid confusion:

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_62/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_62/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_62/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_62/training_3.csv", index_col=0)

df0 = df0.rename(columns={'Wins': '2013 Wins', 'Losses': '2013 Losses', 'Draws': '2013 Draws'})
df1 = df1.rename(columns={'Wins': '2014 Wins', 'Losses': '2014 Losses', 'Draws': '2014 Draws'})
df2 = df2.rename(columns={'Wins': '2015 Wins', 'Losses': '2015 Losses', 'Draws': '2015 Draws'})
df3 = df3.rename(columns={'Wins': '2016 Wins', 'Losses': '2016 Losses', 'Draws': '2016 Draws'})

df = df0.merge(df1, on='Wrestler', how='outer')
df = df.merge(df2, on='Wrestler', how='outer')
df = df.merge(df3, on='Wrestler', how='outer')

df = df[['Wrestler', '2013 Wins', '2013 Losses', '2013 Draws',
         '2014 Wins', '2014 Losses', '2014 Draws',
         '2015 Wins', '2015 Losses', '2015 Draws',
         '2016 Wins', '2016 Losses', '2016 Draws']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length3_62/target_multisource_mcts.csv")