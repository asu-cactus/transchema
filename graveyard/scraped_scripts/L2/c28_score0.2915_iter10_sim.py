import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_28/training_1.csv", index_col=0)

df1['IsHoliday'] = df1['IsHoliday'].astype(int)

agg_df = df1.groupby(['Store', 'Dept', 'IsHoliday'], as_index=False)['Weekly_Sales'].sum()

df0_agg = df0.groupby(['Store', 'StoreType', 'Assortment'], as_index=False).agg({
    'CompetitionDistance': 'mean',
    'CompetitionOpenSinceMonth': 'max',
    'CompetitionOpenSinceYear': 'max',
    'Promo2': 'max',
    'Promo2SinceWeek': 'max',
    'Promo2SinceYear': 'max',
    'PromoInterval': lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan
})

merged = pd.merge(agg_df, df0_agg, on='Store', how='left')

merged['Assortment'] = merged['Assortment'].map({'a': 0, 'b': 1, 'c': 2}).fillna(-1).astype(int)
merged['StoreType'] = merged['StoreType'].map({'a': 0, 'b': 1, 'c': 2, 'd': 3}).fillna(-1).astype(int)

merged['IsHoliday'] = merged['IsHoliday'].astype(int)
merged['Weekly_Sales'] = merged['Weekly_Sales'].round().astype(int)
merged['CompetitionDistance'] = merged['CompetitionDistance'].round().astype('Int64')
merged['CompetitionOpenSinceMonth'] = merged['CompetitionOpenSinceMonth'].astype('Int64')
merged['CompetitionOpenSinceYear'] = merged['CompetitionOpenSinceYear'].astype('Int64')
merged['Promo2'] = merged['Promo2'].astype('Int64')
merged['Promo2SinceWeek'] = merged['Promo2SinceWeek'].astype('Int64')
merged['Promo2SinceYear'] = merged['Promo2SinceYear'].astype('Int64')

def promo_interval_to_int(pi):
    if pd.isna(pi):
        return pd.NA
    mapping = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
    parts = str(pi).split(',')
    if len(parts) == 0:
        return pd.NA
    return mapping.get(parts[0][:3], pd.NA)

merged['PromoInterval'] = merged['PromoInterval'].apply(promo_interval_to_int).astype('Int64')

merged = merged[['StoreType', 'Store', 'Dept', 'Weekly_Sales', 'IsHoliday', 'Assortment',
                 'CompetitionDistance', 'CompetitionOpenSinceMonth', 'CompetitionOpenSinceYear',
                 'Promo2', 'Promo2SinceWeek', 'Promo2SinceYear', 'PromoInterval']]

merged.to_csv("autopipeline-benchmarks/github-pipelines/length2_28/target_multisource_mcts.csv", index=False)