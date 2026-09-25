import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_28/training_1.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_28/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_28/training_0.csv", index_col=0)

df_union = pd.concat([df0, df1], ignore_index=True)

df_merged = pd.merge(df_union, df2, on="Store", how="inner")

df_merged['StoreType'] = df_merged['StoreType'].astype(str)
df_merged['Store'] = pd.to_numeric(df_merged['Store'], errors='coerce').fillna(0).astype(int)
df_merged['Dept'] = pd.to_numeric(df_merged['Dept'], errors='coerce').fillna(0).astype(int)
df_merged['Weekly_Sales'] = pd.to_numeric(df_merged['Weekly_Sales'], errors='coerce').fillna(0).astype(int)
df_merged['IsHoliday'] = df_merged['IsHoliday'].map({True:1, False:0}).fillna(0).astype(int)
df_merged['Assortment'] = df_merged['Assortment'].astype(str).map({'a':1, 'b':2, 'c':3}).fillna(0).astype(int)
df_merged['CompetitionDistance'] = pd.to_numeric(df_merged['CompetitionDistance'], errors='coerce').fillna(0).astype(int)
df_merged['CompetitionOpenSinceMonth'] = pd.to_numeric(df_merged['CompetitionOpenSinceMonth'], errors='coerce').fillna(0).astype(int)
df_merged['CompetitionOpenSinceYear'] = pd.to_numeric(df_merged['CompetitionOpenSinceYear'], errors='coerce').fillna(0).astype(int)
df_merged['Promo2'] = pd.to_numeric(df_merged['Promo2'], errors='coerce').fillna(0).astype(int)
df_merged['Promo2SinceWeek'] = pd.to_numeric(df_merged['Promo2SinceWeek'], errors='coerce').fillna(0).astype(int)
df_merged['Promo2SinceYear'] = pd.to_numeric(df_merged['Promo2SinceYear'], errors='coerce').fillna(0).astype(int)
df_merged['PromoInterval'] = df_merged['PromoInterval'].fillna("").astype(str)

result = df_merged[['StoreType', 'Store', 'Dept', 'Weekly_Sales', 'IsHoliday', 'Assortment', 'CompetitionDistance', 'CompetitionOpenSinceMonth', 'CompetitionOpenSinceYear', 'Promo2', 'Promo2SinceWeek', 'Promo2SinceYear', 'PromoInterval']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_28/target_multisource_mcts.csv", index=False)