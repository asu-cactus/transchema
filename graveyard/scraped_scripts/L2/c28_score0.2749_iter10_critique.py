import pandas as pd
import numpy as np

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_28/training_1.csv", index_col=0)

# Convert IsHoliday to int
df1['IsHoliday'] = df1['IsHoliday'].astype(int)

# Join on 'Store'
merged = pd.merge(df0, df1, on='Store', how='inner')

# Define a function to get mode safely
def mode_or_nan(series):
    m = series.mode()
    if m.empty:
        return pd.NA
    else:
        return m.iloc[0]

# Group by the leftmost columns of target schema that are non-float and unique
group_cols = ['StoreType', 'Store', 'Dept', 'IsHoliday', 'Assortment']

agg_dict = {
    'Weekly_Sales': 'sum',
    'CompetitionDistance': 'mean',
    'CompetitionOpenSinceMonth': 'max',
    'CompetitionOpenSinceYear': 'max',
    'Promo2': 'max',
    'Promo2SinceWeek': 'max',
    'Promo2SinceYear': 'max',
    'PromoInterval': mode_or_nan
}

agg_df = merged.groupby(group_cols, as_index=False).agg(agg_dict)

# Map categorical string columns to integers as per target schema
agg_df['Assortment'] = agg_df['Assortment'].map({'a': 0, 'b': 1, 'c': 2}).fillna(-1).astype(int)
agg_df['StoreType'] = agg_df['StoreType'].map({'a': 0, 'b': 1, 'c': 2, 'd': 3}).fillna(-1).astype(int)

# Convert types to match target schema
agg_df['IsHoliday'] = agg_df['IsHoliday'].astype(int)
agg_df['Weekly_Sales'] = agg_df['Weekly_Sales'].round().astype(int)
agg_df['CompetitionDistance'] = agg_df['CompetitionDistance'].round().astype('Int64')
agg_df['CompetitionOpenSinceMonth'] = agg_df['CompetitionOpenSinceMonth'].astype('Int64')
agg_df['CompetitionOpenSinceYear'] = agg_df['CompetitionOpenSinceYear'].astype('Int64')
agg_df['Promo2'] = agg_df['Promo2'].astype('Int64')
agg_df['Promo2SinceWeek'] = agg_df['Promo2SinceWeek'].astype('Int64')
agg_df['Promo2SinceYear'] = agg_df['Promo2SinceYear'].astype('Int64')

# Convert PromoInterval string to integer month
def promo_interval_to_int(pi):
    if pd.isna(pi):
        return pd.NA
    mapping = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6,
               'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
    parts = str(pi).split(',')
    if len(parts) == 0:
        return pd.NA
    return mapping.get(parts[0][:3], pd.NA)

agg_df['PromoInterval'] = agg_df['PromoInterval'].apply(promo_interval_to_int).astype('Int64')

# Reorder columns to match target schema exactly
agg_df = agg_df[['StoreType', 'Store', 'Dept', 'Weekly_Sales', 'IsHoliday', 'Assortment',
                 'CompetitionDistance', 'CompetitionOpenSinceMonth', 'CompetitionOpenSinceYear',
                 'Promo2', 'Promo2SinceWeek', 'Promo2SinceYear', 'PromoInterval']]

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length2_28/target_multisource_mcts.csv", index=False)