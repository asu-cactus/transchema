import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_2/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_2/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_2/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

merged = pd.merge(df0, df1, on="calaccess_committee_id", how="inner")

result = merged[[
    "contributor_firstname",
    "contributor_lastname",
    "committee_position",
    "amount"
]].copy()

result["contributor_firstname"] = result["contributor_firstname"].astype(str)
result["contributor_lastname"] = result["contributor_lastname"].astype(str)
result["committee_position"] = result["committee_position"].astype(str)
result["amount"] = result["amount"].astype(float)

result.to_csv(target_path, index=False)