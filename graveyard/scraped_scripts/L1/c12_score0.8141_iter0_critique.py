import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_12/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_12/training_1.csv", index_col=0)

# Deduplicate df1 on Athlete to avoid row multiplication in join
df1 = df1.drop_duplicates(subset=["Athlete"])

df = pd.merge(df0, df1, on="Athlete", how="left")

df["Age"] = df["Age"].astype(float)
df["Year"] = df["Year"].astype("Int64")
df["Closing Ceremony Date"] = df["Closing Ceremony Date"].astype(str)
df["Gold Medals"] = df["Gold Medals"].astype("Int64")
df["Silver Medals"] = df["Silver Medals"].astype("Int64")
df["Bronze Medals"] = df["Bronze Medals"].astype("Int64")
df["Total Medals"] = df["Total Medals"].astype("Int64")
df["Country"] = df["Country"].astype(str)

df = df[['Athlete', 'Age', 'Year', 'Closing Ceremony Date', 'Gold Medals', 'Silver Medals', 'Bronze Medals', 'Total Medals', 'Country']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_12/target_multisource_mcts.csv", index=False)