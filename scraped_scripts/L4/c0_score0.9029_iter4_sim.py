import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_3.csv", index_col=0)

join_0_2 = pd.merge(source0, source2, on="COD_PERSONA", how="inner")
join_all = pd.merge(join_0_2, source3, left_on="COD_OFICIPAL", right_on="COD_OFICI", how="inner")

result = join_all.groupby("des_territ", dropna=False, as_index=False).size()
result = result.rename(columns={"des_territ": "des_territ"})

result[["des_territ"]].to_csv("autopipeline-benchmarks/github-pipelines/length4_0/target_multisource_mcts.csv", index=False)