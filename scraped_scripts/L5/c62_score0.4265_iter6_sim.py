import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_62/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_62/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_62/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_62/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_62/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df["Age Group"] = df["Age Group"].astype(str).str.extract(r'(\d+)').astype(int)
df["Sex"] = df["Sex"].astype(str)

cols = ["Sex", "Age Group", "Don't know/Refused/Missing", "Normal Weight", "Obese", "Overweight", "Underweight"]
df = df[cols]

for c in cols[2:]:
    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_62/target_multisource_mcts.csv", index=False)