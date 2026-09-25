import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_8/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_8/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_8/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_8/training_3.csv", index_col=0)

s0 = s0.rename(columns={"Wins": "2013 Wins", "Losses": "2013 Losses", "Draws": "2013 Draws"})
s1 = s1.rename(columns={"Wins": "2014 Wins", "Losses": "2014 Losses", "Draws": "2014 Draws"})
s2 = s2.rename(columns={"Wins": "2015 Wins", "Losses": "2015 Losses", "Draws": "2015 Draws"})
s3 = s3.rename(columns={"Wins": "2016 Wins", "Losses": "2016 Losses", "Draws": "2016 Draws"})

df = s0.merge(s1, on="Wrestler", how="outer")
df = df.merge(s2, on="Wrestler", how="outer")
df = df.merge(s3, on="Wrestler", how="outer")

cols = ['2013 Wins', '2013 Losses', '2013 Draws', '2014 Wins', '2014 Losses', '2014 Draws',
        '2015 Wins', '2015 Losses', '2015 Draws', '2016 Wins', '2016 Losses', '2016 Draws']

for c in cols:
    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).astype(int)

df = df[['Wrestler'] + cols]

df.to_csv("autopipeline-benchmarks/github-pipelines/length3_8/target_multisource_mcts.csv", index=False)