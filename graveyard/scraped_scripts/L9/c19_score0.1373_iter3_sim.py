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

r0 = pd.merge(s1, s6, on="Artist", how="outer", suffixes=('_1', '_6'))

# After merge, keep columns from s6 for Year Inducted, Years Waited, # of Years Nominated, Inducted By if present, else from s1
for col in ['Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By']:
    if col+'_6' in r0.columns and col+'_1' in r0.columns:
        r0[col] = r0[col+'_6'].combine_first(r0[col+'_1'])
        r0.drop([col+'_6', col+'_1'], axis=1, inplace=True)
    elif col+'_6' in r0.columns:
        r0[col] = r0[col+'_6']
        r0.drop([col+'_6'], axis=1, inplace=True)
    elif col+'_1' in r0.columns:
        r0[col] = r0[col+'_1']
        r0.drop([col+'_1'], axis=1, inplace=True)

r1 = pd.merge(r0, s0, on="Artist", how="outer")
r2 = pd.merge(r1, s2, on="Artist", how="outer")
r3 = pd.merge(r2, s3, on="Artist", how="outer")
r4 = pd.merge(r3, s4, on="Artist", how="outer")
r5 = pd.merge(r4, s5, on="Artist", how="outer")
r6 = pd.merge(r5, s7, on="Artist", how="outer")
r7 = pd.merge(r6, s8, on="Artist", how="outer")

final_cols = ['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By', 'Influenced',
              'Certified Units (Millions)', 'Albums in RS500', 'Top 100 Singles', 'Highest Position',
              'Times on Cover of RS', 'Score', 'Spotify']

result = r7[final_cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_19/target_multisource_mcts.csv", index=False)