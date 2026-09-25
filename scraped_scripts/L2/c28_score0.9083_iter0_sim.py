import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_28/training_1.csv", index_col=0)

df = pd.merge(df1, df0, on="Store", how="inner")

df_grouped = df.groupby("StoreType", as_index=False).agg({
    "Store": "sum",
    "Dept": "sum",
    "Weekly_Sales": "sum",
    "IsHoliday": lambda x: x.astype(int).sum(),
    "Assortment": lambda x: x.astype('category').cat.codes.sum(),
    "CompetitionDistance": "sum",
    "CompetitionOpenSinceMonth": "sum",
    "CompetitionOpenSinceYear": "sum",
    "Promo2": "sum",
    "Promo2SinceWeek": "sum",
    "Promo2SinceYear": "sum",
    "PromoInterval": lambda x: x.astype('category').cat.codes.sum()
})

df_grouped["IsHoliday"] = df_grouped["IsHoliday"].astype(int)
df_grouped["Assortment"] = df_grouped["Assortment"].astype(int)
df_grouped["PromoInterval"] = df_grouped["PromoInterval"].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_28/target_multisource_mcts.csv", index=False)