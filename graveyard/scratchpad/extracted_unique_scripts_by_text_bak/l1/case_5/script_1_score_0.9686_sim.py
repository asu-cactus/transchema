import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_5/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_5/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_5/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

merged = pd.merge(df0, df1, on="ProvinciaID", how="inner")

result = merged[["ProvinciaID", "ProvinciaNombre", "RegionID", "ComunaID", "ComunaNombre"]]

result.to_csv(target_path, index=False)