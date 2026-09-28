import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_62/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_62/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_62/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_62/training_3.csv", index_col=0)

agg_0 = df0.groupby("Wrestler", as_index=False).agg({"Wins":"sum", "Losses":"sum", "Draws":"sum"})
agg_0.columns = ["Wrestler", "2013 Wins", "2013 Losses", "2013 Draws"]

agg_1 = df1.groupby("Wrestler", as_index=False).agg({"Wins":"sum", "Losses":"sum", "Draws":"sum"})
agg_1.columns = ["Wrestler", "2014 Wins", "2014 Losses", "2014 Draws"]

agg_2 = df2.groupby("Wrestler", as_index=False).agg({"Wins":"sum", "Losses":"sum", "Draws":"sum"})
agg_2.columns = ["Wrestler", "2015 Wins", "2015 Losses", "2015 Draws"]

agg_3 = df3.groupby("Wrestler", as_index=False).agg({"Wins":"sum", "Losses":"sum", "Draws":"sum"})
agg_3.columns = ["Wrestler", "2016 Wins", "2016 Losses", "2016 Draws"]

join_01 = pd.merge(agg_0, agg_1, on="Wrestler", how="inner")
join_012 = pd.merge(join_01, agg_2, on="Wrestler", how="inner")
join_0123 = pd.merge(join_012, agg_3, on="Wrestler", how="inner")

join_0123 = join_0123.fillna(0)
int_cols = join_0123.columns.drop("Wrestler")
join_0123[int_cols] = join_0123[int_cols].astype(int)

join_0123.to_csv("autopipeline-benchmarks/github-pipelines/length3_62/target_multisource_mcts.csv", index=False)