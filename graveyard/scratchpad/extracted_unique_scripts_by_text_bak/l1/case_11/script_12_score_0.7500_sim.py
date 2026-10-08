import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_11/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on="sex")

pivoted = joined.pivot_table(index="sex", values="births_x", aggfunc="sum").reset_index()

pivoted.columns = ["sex", "births"]

pivoted["births"] = pivoted["births"].astype(int)

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length1_11/target_multisource_mcts.csv", index=False)