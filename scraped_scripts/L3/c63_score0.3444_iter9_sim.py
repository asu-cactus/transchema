import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_63/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_63/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_63/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_63/training_3.csv", index_col=0)

agg0 = df0.groupby("Wrestler", as_index=False).agg({"Wins":"sum", "Losses":"sum", "Draws":"sum"})
agg1 = df1.groupby("Wrestler", as_index=False).agg({"Wins":"sum", "Losses":"sum", "Draws":"sum"})
agg2 = df2.groupby("Wrestler", as_index=False).agg({"Wins":"sum", "Losses":"sum", "Draws":"sum"})
agg3 = df3.groupby("Wrestler", as_index=False).agg({"Wins":"sum", "Losses":"sum", "Draws":"sum"})

join_01 = pd.merge(agg0, agg1, on="Wrestler", how="outer", suffixes=('_2013', '_2014'))
join_012 = pd.merge(join_01, agg2, on="Wrestler", how="outer")
join_012 = join_012.rename(columns={"Wins":"Wins_2015", "Losses":"Losses_2015", "Draws":"Draws_2015"})
final_df = pd.merge(join_012, agg3, on="Wrestler", how="outer", suffixes=('_2015', '_2016'))

final_df = final_df.rename(columns={
    "Wins_2013": "2013 Wins",
    "Losses_2013": "2013 Losses",
    "Draws_2013": "2013 Draws",
    "Wins_2014": "2014 Wins",
    "Losses_2014": "2014 Losses",
    "Draws_2014": "2014 Draws",
    "Wins_2015": "2015 Wins",
    "Losses_2015": "2015 Losses",
    "Draws_2015": "2015 Draws",
    "Wins": "2016 Wins",
    "Losses": "2016 Losses",
    "Draws": "2016 Draws"
})

final_df = final_df[[
    "Wrestler",
    "2013 Wins", "2013 Losses", "2013 Draws",
    "2014 Wins", "2014 Losses", "2014 Draws",
    "2015 Wins", "2015 Losses", "2015 Draws",
    "2016 Wins", "2016 Losses", "2016 Draws"
]]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length3_63/target_multisource_mcts.csv", index=False)