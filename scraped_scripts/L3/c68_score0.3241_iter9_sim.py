import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_68/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_68/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_68/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_68/training_3.csv", index_col=0)

agg_0 = df0.groupby("Wrestler", as_index=False).agg({"Wins":"sum", "Losses":"sum", "Draws":"sum"})
agg_1 = df1.groupby("Wrestler", as_index=False).agg({"Wins":"sum", "Losses":"sum", "Draws":"sum"})
agg_2 = df2.groupby("Wrestler", as_index=False).agg({"Wins":"sum", "Losses":"sum", "Draws":"sum"})
agg_3 = df3.groupby("Wrestler", as_index=False).agg({"Wins":"sum", "Losses":"sum", "Draws":"sum"})

join_01 = pd.merge(agg_0, agg_1, on="Wrestler", how="outer", suffixes=('_2013', '_2014'))
join_012 = pd.merge(join_01, agg_2, on="Wrestler", how="outer")
join_012 = join_012.rename(columns={"Wins":"2015 Wins", "Losses":"2015 Losses", "Draws":"2015 Draws"})
join_012 = join_012.rename(columns={"Wins_2013":"2013 Wins", "Losses_2013":"2013 Losses", "Draws_2013":"2013 Draws",
                                    "Wins_2014":"2014 Wins", "Losses_2014":"2014 Losses", "Draws_2014":"2014 Draws"})

final_df = pd.merge(join_012, agg_3, on="Wrestler", how="outer")
final_df = final_df.rename(columns={"Wins":"2016 Wins", "Losses":"2016 Losses", "Draws":"2016 Draws"})

final_df = final_df[["Wrestler",
                     "2013 Wins", "2013 Losses", "2013 Draws",
                     "2014 Wins", "2014 Losses", "2014 Draws",
                     "2015 Wins", "2015 Losses", "2015 Draws",
                     "2016 Wins", "2016 Losses", "2016 Draws"]]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length3_68/target_multisource_mcts.csv", index=False)