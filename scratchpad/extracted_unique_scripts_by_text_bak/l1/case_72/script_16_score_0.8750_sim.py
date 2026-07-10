import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_72/training_0.csv", index_col=0)

joined = pd.merge(df, df, on="condition")

pivoted = joined.pivot_table(index="condition", columns="click_x", values="click_y", aggfunc='count', fill_value=0)

pivoted.columns = pivoted.columns.astype(str)

pivoted = pivoted.reset_index()

pivoted = pivoted.rename(columns={"0": "0"})

pivoted = pivoted[["condition", "0"]]

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length1_72/target_multisource_mcts.csv", index=False)