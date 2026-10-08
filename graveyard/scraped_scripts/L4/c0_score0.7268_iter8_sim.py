import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_0.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_3.csv", index_col=0)

merged = pd.merge(
    source0,
    source3,
    left_on=["COD_OFICIPAL", "COD_AREANEGO"],
    right_on=["COD_OFICI", "cod_areanego"],
    how="inner"
)

result = merged.groupby("des_territ", dropna=False).size().reset_index(name="count")

final = result[["des_territ"]]

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_0/target_multisource_mcts.csv", index=False)