import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_86/test_0.csv", index_col=0)
aggregated = df.groupby("neighbourhood")["price"].count().reset_index(name="price_24")
aggregated.to_csv("autopipeline-benchmarks/github-pipelines/length1_86/target_multisource_mcts_recovery_test_val.csv", index=False)