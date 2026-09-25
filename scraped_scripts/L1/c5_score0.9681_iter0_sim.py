import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_5/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_5/training_1.csv", index_col=0)

result = pd.merge(df0, df1, on="ProvinciaID")

result = result[['ProvinciaID', 'ProvinciaNombre', 'RegionID', 'ComunaID', 'ComunaNombre']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_5/target_multisource_mcts.csv", index=False)