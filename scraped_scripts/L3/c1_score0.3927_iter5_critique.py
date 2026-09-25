import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_3.csv", index_col=0)

s0 = s0.rename(columns={"Wins": "2013 Wins", "Losses": "2013 Losses", "Draws": "2013 Draws"})
s1 = s1.rename(columns={"Wins": "2014 Wins", "Losses": "2014 Losses", "Draws": "2014 Draws"})
s2 = s2.rename(columns={"Wins": "2015 Wins", "Losses": "2015 Losses", "Draws": "2015 Draws"})
s3 = s3.rename(columns={"Wins": "2016 Wins", "Losses": "2016 Losses", "Draws": "2016 Draws"})

df = s0.merge(s1, on="Wrestler", how="outer")
df = df.merge(s2, on="Wrestler", how="outer")
df = df.merge(s3, on="Wrestler", how="outer")

# Cast all numeric columns to nullable integer type to match target schema
df = df.astype({
    '2013 Wins': 'Int64', '2013 Losses': 'Int64', '2013 Draws': 'Int64',
    '2014 Wins': 'Int64', '2014 Losses': 'Int64', '2014 Draws': 'Int64',
    '2015 Wins': 'Int64', '2015 Losses': 'Int64', '2015 Draws': 'Int64',
    '2016 Wins': 'Int64', '2016 Losses': 'Int64', '2016 Draws': 'Int64'
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length3_1/target_multisource_mcts.csv", index=False)