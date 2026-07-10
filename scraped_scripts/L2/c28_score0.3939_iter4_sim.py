import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_28/training_1.csv", index_col=0)

df = pd.merge(df1, df0, on="Store", how="inner")

df['StoreType'] = df['StoreType'].astype(str)
df['Store'] = df['Store'].astype(int)
df['Dept'] = df['Dept'].astype(int)
df['Weekly_Sales'] = df['Weekly_Sales'].astype(int)
df['IsHoliday'] = df['IsHoliday'].astype(int)
df['Assortment'] = df['Assortment'].astype(str).map({'a':1, 'b':2, 'c':3}).fillna(0).astype(int)
df['CompetitionDistance'] = df['CompetitionDistance'].fillna(0).astype(int)
df['CompetitionOpenSinceMonth'] = df['CompetitionOpenSinceMonth'].fillna(0).astype(int)
df['CompetitionOpenSinceYear'] = df['CompetitionOpenSinceYear'].fillna(0).astype(int)
df['Promo2'] = df['Promo2'].fillna(0).astype(int)
df['Promo2SinceWeek'] = df['Promo2SinceWeek'].fillna(0).astype(int)
df['Promo2SinceYear'] = df['Promo2SinceYear'].fillna(0).astype(int)

def promo_interval_to_int(pi):
    if pd.isna(pi):
        return 0
    return 1
df['PromoInterval'] = df['PromoInterval'].apply(promo_interval_to_int).astype(int)

df = df[['StoreType', 'Store', 'Dept', 'Weekly_Sales', 'IsHoliday', 'Assortment', 'CompetitionDistance',
         'CompetitionOpenSinceMonth', 'CompetitionOpenSinceYear', 'Promo2', 'Promo2SinceWeek',
         'Promo2SinceYear', 'PromoInterval']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_28/target_multisource_mcts.csv", index=False)