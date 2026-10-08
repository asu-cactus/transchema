import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_8.csv", index_col=0)

df = pd.merge(s1, s6, on="Artist", how="outer", suffixes=('', '_drop'))
df = df.loc[:, ~df.columns.str.endswith('_drop')]

df = pd.merge(df, s0, on="Artist", how="outer")
df = pd.merge(df, s2, on="Artist", how="outer")
df = pd.merge(df, s3, on="Artist", how="outer")
df = pd.merge(df, s4, on="Artist", how="outer")
df = pd.merge(df, s5, on="Artist", how="outer")
df = pd.merge(df, s7, on="Artist", how="outer")
df = pd.merge(df, s8, on="Artist", how="outer")

df = df[['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By', 'Influenced',
         'Certified Units (Millions)', 'Albums in RS500', 'Top 100 Singles', 'Highest Position',
         'Times on Cover of RS', 'Score', 'Spotify']]

df['Year Inducted'] = pd.to_numeric(df['Year Inducted'], errors='coerce')
df['Years Waited'] = pd.to_numeric(df['Years Waited'], errors='coerce').astype('Int64')
df['# of Years Nominated'] = pd.to_numeric(df['# of Years Nominated'], errors='coerce').astype('Int64')
df['Influenced'] = pd.to_numeric(df['Influenced'], errors='coerce').astype('Int64')
df['Certified Units (Millions)'] = pd.to_numeric(df['Certified Units (Millions)'], errors='coerce')
df['Albums in RS500'] = pd.to_numeric(df['Albums in RS500'], errors='coerce').astype('Int64')
df['Top 100 Singles'] = pd.to_numeric(df['Top 100 Singles'], errors='coerce').astype('Int64')
df['Highest Position'] = pd.to_numeric(df['Highest Position'], errors='coerce').astype('Int64')
df['Times on Cover of RS'] = pd.to_numeric(df['Times on Cover of RS'], errors='coerce').astype('Int64')
df['Score'] = pd.to_numeric(df['Score'], errors='coerce')
df['Spotify'] = pd.to_numeric(df['Spotify'], errors='coerce').astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_19/target_multisource_mcts.csv", index=False)