import pandas as pd
import numpy as np

# Read source tables
df_sales = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_28/training_1.csv", index_col=0)
df_store = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_28/training_0.csv", index_col=0)

# Join on 'Store'
df = pd.merge(df_sales, df_store, on="Store", how="inner")

# Convert and map columns according to target schema

# StoreType: string, map to string as is
df['StoreType'] = df['StoreType'].astype(str)

# Store: integer
df['Store'] = pd.to_numeric(df['Store'], errors='coerce').fillna(0).astype(int)

# Dept: integer
df['Dept'] = pd.to_numeric(df['Dept'], errors='coerce').fillna(0).astype(int)

# Weekly_Sales: integer (sum aggregation later)
df['Weekly_Sales'] = pd.to_numeric(df['Weekly_Sales'], errors='coerce').fillna(0).astype(int)

# IsHoliday: boolean to int
df['IsHoliday'] = df['IsHoliday'].map({True:1, False:0}).fillna(0).astype(int)

# Assortment: categorical string to int mapping
df['Assortment'] = df['Assortment'].astype(str).map({'a':1, 'b':2, 'c':3}).fillna(0).astype(int)

# CompetitionDistance: integer
df['CompetitionDistance'] = pd.to_numeric(df['CompetitionDistance'], errors='coerce').fillna(0).astype(int)

# CompetitionOpenSinceMonth: integer
df['CompetitionOpenSinceMonth'] = pd.to_numeric(df['CompetitionOpenSinceMonth'], errors='coerce').fillna(0).astype(int)

# CompetitionOpenSinceYear: integer
df['CompetitionOpenSinceYear'] = pd.to_numeric(df['CompetitionOpenSinceYear'], errors='coerce').fillna(0).astype(int)

# Promo2: integer
df['Promo2'] = pd.to_numeric(df['Promo2'], errors='coerce').fillna(0).astype(int)

# Promo2SinceWeek: integer
df['Promo2SinceWeek'] = pd.to_numeric(df['Promo2SinceWeek'], errors='coerce').fillna(0).astype(int)

# Promo2SinceYear: integer
df['Promo2SinceYear'] = pd.to_numeric(df['Promo2SinceYear'], errors='coerce').fillna(0).astype(int)

# PromoInterval: categorical string to int mapping
# Fill NaN with empty string first
df['PromoInterval'] = df['PromoInterval'].fillna("").astype(str)
# Map unique PromoInterval strings to integers
promo_interval_codes, uniques = pd.factorize(df['PromoInterval'])
df['PromoInterval'] = promo_interval_codes.astype(int)

# Group by StoreType, Store, Dept
group_cols = ['StoreType', 'Store', 'Dept']

agg_dict = {
    'Weekly_Sales': 'sum',
    'IsHoliday': 'max',
    'Assortment': 'max',
    'CompetitionDistance': 'max',
    'CompetitionOpenSinceMonth': 'max',
    'CompetitionOpenSinceYear': 'max',
    'Promo2': 'max',
    'Promo2SinceWeek': 'max',
    'Promo2SinceYear': 'max',
    'PromoInterval': 'max'
}

result = df.groupby(group_cols, as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
result = result[['StoreType', 'Store', 'Dept', 'Weekly_Sales', 'IsHoliday', 'Assortment',
                 'CompetitionDistance', 'CompetitionOpenSinceMonth', 'CompetitionOpenSinceYear',
                 'Promo2', 'Promo2SinceWeek', 'Promo2SinceYear', 'PromoInterval']]

# Ensure types exactly as target schema
result['StoreType'] = result['StoreType'].astype(str)
result['Store'] = result['Store'].astype(int)
result['Dept'] = result['Dept'].astype(int)
result['Weekly_Sales'] = result['Weekly_Sales'].astype(int)
result['IsHoliday'] = result['IsHoliday'].astype(int)
result['Assortment'] = result['Assortment'].astype(int)
result['CompetitionDistance'] = result['CompetitionDistance'].astype(int)
result['CompetitionOpenSinceMonth'] = result['CompetitionOpenSinceMonth'].astype(int)
result['CompetitionOpenSinceYear'] = result['CompetitionOpenSinceYear'].astype(int)
result['Promo2'] = result['Promo2'].astype(int)
result['Promo2SinceWeek'] = result['Promo2SinceWeek'].astype(int)
result['Promo2SinceYear'] = result['Promo2SinceYear'].astype(int)
result['PromoInterval'] = result['PromoInterval'].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length2_28/target_multisource_mcts.csv", index=False)