import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_4.csv", index_col=0)

# The partial plan suggests UNION of [Source5_86_0, Source5_86_1, Source5_86_2, Source5_86_3, Source5_86_4]
# But these sources have different schemas, so UNION is not possible directly.
# Instead, the only source that contains the 'Profit' column is Source5_86_2.
# The target schema is ['Profit': integer].
# So the correct approach is to extract 'Profit' column from Source5_86_2, convert to int, and save.

target = s2[['Profit']].copy()
target['Profit'] = target['Profit'].round().astype('Int64')

target.to_csv("autopipeline-benchmarks/github-pipelines/length5_86/target_multisource_mcts.csv", index=False)