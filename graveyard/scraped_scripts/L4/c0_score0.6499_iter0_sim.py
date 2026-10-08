import pandas as pd

src3_path = "autopipeline-benchmarks/github-pipelines/length4_0/training_3.csv"

df3 = pd.read_csv(src3_path, index_col=0)
result = df3.groupby("des_territ", dropna=False, as_index=False).size()
result = result.rename(columns={"des_territ": "des_territ"})

result[["des_territ"]].to_csv("autopipeline-benchmarks/github-pipelines/length4_0/target_multisource_mcts.csv", index=False)