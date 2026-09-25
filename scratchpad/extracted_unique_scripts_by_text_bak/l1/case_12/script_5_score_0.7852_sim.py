import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_12/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_12/training_1.csv", index_col=0)

df = pd.merge(df0, df1, on="Athlete", how="inner")

df["Age"] = df["Age"].astype(float)
df["Year"] = df["Year"].astype(int)
df["Gold Medals"] = df["Gold Medals"].astype(int)
df["Silver Medals"] = df["Silver Medals"].astype(int)
df["Bronze Medals"] = df["Bronze Medals"].astype(int)
df["Total Medals"] = df["Total Medals"].astype(int)
df["Closing Ceremony Date"] = df["Closing Ceremony Date"].astype(str)
df["Country"] = df["Country"].astype(str)
df["Athlete"] = df["Athlete"].astype(str)

df = df[['Athlete', 'Age', 'Year', 'Closing Ceremony Date', 'Gold Medals', 'Silver Medals', 'Bronze Medals', 'Total Medals', 'Country']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_12/target_multisource_mcts.csv")