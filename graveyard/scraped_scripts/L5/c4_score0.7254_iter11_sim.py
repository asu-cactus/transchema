import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_1.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_3.csv", index_col=0)

join_01 = pd.merge(source0, source1, on="Artist", how="inner")
join_013 = pd.merge(join_01, source3, on="Artist", how="inner")

join_013 = join_013.astype({
    "Year Inducted": "float",
    "Years Waited": "Int64",
    "# of Years Nominated": "Int64",
    "Influenced": "Int64",
    "Certified Units (Millions)": "float"
})

join_013 = join_013[[
    "Artist",
    "Year Inducted",
    "Years Waited",
    "# of Years Nominated",
    "Inducted By",
    "Influenced",
    "Certified Units (Millions)"
]]

join_013.to_csv("autopipeline-benchmarks/github-pipelines/length5_4/target_multisource_mcts.csv", index=False)