import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_23/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_23/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_23/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_23/training_3.csv", index_col=0)

agg_0 = df0.groupby("Wrestler", as_index=False).agg({"Wins":"sum", "Losses":"sum", "Draws":"sum"})
agg_1 = df1.groupby("Wrestler", as_index=False).agg({"Wins":"sum", "Losses":"sum", "Draws":"sum"})
agg_2 = df2.groupby("Wrestler", as_index=False).agg({"Wins":"sum", "Losses":"sum", "Draws":"sum"})
agg_3 = df3.groupby("Wrestler", as_index=False).agg({"Wins":"sum", "Losses":"sum", "Draws":"sum"})

join_01 = pd.merge(agg_0, agg_1, on="Wrestler", how="outer", suffixes=("", "_1"))
join_012 = pd.merge(join_01, agg_2, on="Wrestler", how="outer", suffixes=("", "_2"))
join_0123 = pd.merge(join_012, agg_3, on="Wrestler", how="outer", suffixes=("", "_3"))

join_0123 = join_0123.rename(columns={
    "Wins": "2013 Wins", "Losses": "2013 Losses", "Draws": "2013 Draws",
    "Wins_1": "2014 Wins", "Losses_1": "2014 Losses", "Draws_1": "2014 Draws",
    "Wins_2": "2015 Wins", "Losses_2": "2015 Losses", "Draws_2": "2015 Draws",
    "Wins_3": "2016 Wins", "Losses_3": "2016 Losses", "Draws_3": "2016 Draws"
})

join_0123.to_csv("autopipeline-benchmarks/github-pipelines/length3_23/target_multisource_mcts.csv", index=False)