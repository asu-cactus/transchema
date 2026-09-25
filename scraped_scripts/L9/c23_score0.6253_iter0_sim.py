import pandas as pd

src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_3.csv", index_col=0)
src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_6.csv", index_col=0)
src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_8.csv", index_col=0)

df = pd.concat([src2, src3, src6, src8], ignore_index=True)

result = df[['MONTHS_AGE']].copy()
result['MONTHS_AGE'] = result['MONTHS_AGE'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_23/target_multisource_mcts.csv", index=False)