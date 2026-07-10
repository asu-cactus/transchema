import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_62/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_62/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_62/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_62/training_3.csv", index_col=0)

g0 = df0.groupby("Wrestler", as_index=False).agg({"Wins":"sum", "Losses":"sum", "Draws":"sum"})
g1 = df1.groupby("Wrestler", as_index=False).agg({"Wins":"sum", "Losses":"sum", "Draws":"sum"})
g2 = df2.groupby("Wrestler", as_index=False).agg({"Wins":"sum", "Losses":"sum", "Draws":"sum"})
g3 = df3.groupby("Wrestler", as_index=False).agg({"Wins":"sum", "Losses":"sum", "Draws":"sum"})

g0 = g0.rename(columns={"Wins":"2013 Wins", "Losses":"2013 Losses", "Draws":"2013 Draws"})
g1 = g1.rename(columns={"Wins":"2014 Wins", "Losses":"2014 Losses", "Draws":"2014 Draws"})
g2 = g2.rename(columns={"Wins":"2015 Wins", "Losses":"2015 Losses", "Draws":"2015 Draws"})
g3 = g3.rename(columns={"Wins":"2016 Wins", "Losses":"2016 Losses", "Draws":"2016 Draws"})

df = pd.merge(g0, g1, on="Wrestler", how="outer")
df = pd.merge(df, g2, on="Wrestler", how="outer")
df = pd.merge(df, g3, on="Wrestler", how="outer")

int_cols = [col for col in df.columns if col != "Wrestler"]
df[int_cols] = df[int_cols].fillna(0).astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length3_62/target_multisource_mcts.csv", index=False)