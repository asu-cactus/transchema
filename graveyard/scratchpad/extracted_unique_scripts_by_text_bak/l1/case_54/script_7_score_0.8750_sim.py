import pandas as pd

source_path = "autopipeline-benchmarks/github-pipelines/length1_54/training_0.csv"
df = pd.read_csv(source_path, index_col=0)

joined = pd.merge(df, df, on="condition", suffixes=('_left', '_right'))

grouped = joined.groupby("condition", as_index=False).agg({"click_left": "sum"})

grouped.rename(columns={"click_left": "click"}, inplace=True)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_54/target_multisource_mcts.csv", index=False)