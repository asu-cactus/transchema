import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_87/training_0.csv", index_col=0)

# Extract last name by splitting on ',' and taking the first part, strip spaces
df0["Name"] = df0["Name"].str.split(",", n=1).str[0].str.strip()

# Group by Name to get unique last names
result = df0[["Name"]].drop_duplicates().reset_index(drop=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_87/target_multisource_mcts.csv", index=False)