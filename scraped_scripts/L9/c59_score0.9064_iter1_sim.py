import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_59/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_59/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_59/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_59/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_59/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_59/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_59/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_59/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_59/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_59/training_9.csv", index_col=0)
s10 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_59/training_10.csv", index_col=0)
s11 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_59/training_11.csv", index_col=0)
s12 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_59/training_12.csv", index_col=0)
s13 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_59/training_13.csv", index_col=0)
s14 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_59/training_14.csv", index_col=0)
s15 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_59/training_15.csv", index_col=0)
s16 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_59/training_16.csv", index_col=0)

joined_4_14 = pd.merge(s4, s14, on="country", how="inner", suffixes=('_4', '_14'))
joined_4_14 = joined_4_14[['country', 'cpi_4']].rename(columns={'cpi_4': 'cpi'})

union_all = pd.concat([
    s0, s1, s2, s3, s5, s6, s7, s8, s9, s10, s11, s12, s13, joined_4_14
], ignore_index=True)

union_all['country'] = union_all['country'].astype(str)
union_all['cpi'] = union_all['cpi'].astype(float)

union_all.to_csv("autopipeline-benchmarks/github-pipelines/length9_59/target_multisource_mcts.csv", index=False)