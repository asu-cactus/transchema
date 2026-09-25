import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_12/training_0.csv")
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_12/training_1.csv")

df = pd.merge(df0, df1, on="Athlete", how="left")

df = df.astype({
    "Age": "float",
    "Year": "int",
    "Gold Medals": "int",
    "Silver Medals": "int",
    "Bronze Medals": "int",
    "Total Medals": "int",
    "Country": "string",
    "Closing Ceremony Date": "string"
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_12/target_multisource_mcts.csv", index=False)