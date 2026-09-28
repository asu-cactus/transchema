import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_92/training_0.csv", index_col=0)

pivoted = df0.pivot(index='country', columns='year', values=['NY.GDP.MKTP.KN', 'SI.DST.10TH.10', 'SP.POP.TOTL'])

pivoted.columns = [f"{col[0]}_{col[1]}" for col in pivoted.columns]

pivoted = pivoted.reset_index()

years = sorted(df0['year'].unique())
if len(years) >= 2:
    y1, y2 = years[0], years[1]
else:
    y1 = y2 = years[0]

pivoted = pivoted.rename(columns={
    f"NY.GDP.MKTP.KN_{y1}": "NY.GDP.MKTP.KN_x",
    f"SI.DST.10TH.10_{y1}": "SI.DST.10TH.10_x",
    f"SP.POP.TOTL_{y1}": "SP.POP.TOTL_x",
    f"NY.GDP.MKTP.KN_{y2}": "NY.GDP.MKTP.KN_y",
    f"SI.DST.10TH.10_{y2}": "SI.DST.10TH.10_y",
    f"SP.POP.TOTL_{y2}": "SP.POP.TOTL_y",
})

pivoted["NY.GDP.MKTP.KN"] = pivoted[["NY.GDP.MKTP.KN_x", "NY.GDP.MKTP.KN_y"]].mean(axis=1)
pivoted["SI.DST.10TH.10"] = pivoted[["SI.DST.10TH.10_x", "SI.DST.10TH.10_y"]].mean(axis=1)
pivoted["SP.POP.TOTL"] = pivoted[["SP.POP.TOTL_x", "SP.POP.TOTL_y"]].mean(axis=1)

pivoted = pivoted[['country',
                   'NY.GDP.MKTP.KN_x', 'SI.DST.10TH.10_x', 'SP.POP.TOTL_x',
                   'NY.GDP.MKTP.KN_y', 'SI.DST.10TH.10_y', 'SP.POP.TOTL_y',
                   'NY.GDP.MKTP.KN', 'SI.DST.10TH.10', 'SP.POP.TOTL']]

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length5_92/target_multisource_mcts.csv", index=False)