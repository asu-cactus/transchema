import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_53/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_53/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_53/training_2.csv", index_col=0)

union_result = pd.concat([source0, source2], ignore_index=True)

merged = pd.merge(union_result, source1, on="Athlete", how="inner")

result = merged[[
    "Athlete",
    "Age",
    "Year",
    "Closing Ceremony Date",
    "Gold Medals",
    "Silver Medals",
    "Bronze Medals",
    "Total Medals",
    "Country",
    "Sport"
]]

result["Age"] = result["Age"].astype(float)
result["Year"] = result["Year"].astype(int)
result["Gold Medals"] = result["Gold Medals"].astype(int)
result["Silver Medals"] = result["Silver Medals"].astype(int)
result["Bronze Medals"] = result["Bronze Medals"].astype(int)
result["Total Medals"] = result["Total Medals"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_53/target_multisource_mcts.csv", index=False)