import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_28/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_28/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_28/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Convert IsHoliday to int
df1['IsHoliday'] = df1['IsHoliday'].astype(int)

# Join on Store
merged = pd.merge(df1, df0, on='Store', how='inner')

# Define aggregation dictionary
agg_dict = {
    'Weekly_Sales': 'sum',
    'IsHoliday': 'sum',
    'Dept': 'sum',
    'Assortment': 'first',
    'CompetitionDistance': 'first',
    'CompetitionOpenSinceMonth': 'first',
    'CompetitionOpenSinceYear': 'first',
    'Promo2': 'first',
    'Promo2SinceWeek': 'first',
    'Promo2SinceYear': 'first',
    'PromoInterval': 'first',
    'StoreType': 'first'
}

# Group by StoreType and Store
grouped = merged.groupby(['StoreType', 'Store'], as_index=False).agg(agg_dict)

# Map categorical columns to integers
grouped['Assortment'] = grouped['Assortment'].map({'a': 0, 'b': 1, 'c': 2}).fillna(-1).astype(int)
grouped['Promo2'] = grouped['Promo2'].astype(int)
grouped['Promo2SinceWeek'] = grouped['Promo2SinceWeek'].fillna(0).astype(int)
grouped['Promo2SinceYear'] = grouped['Promo2SinceYear'].fillna(0).astype(int)
grouped['CompetitionDistance'] = grouped['CompetitionDistance'].fillna(0).astype(int)
grouped['CompetitionOpenSinceMonth'] = grouped['CompetitionOpenSinceMonth'].fillna(0).astype(int)
grouped['CompetitionOpenSinceYear'] = grouped['CompetitionOpenSinceYear'].fillna(0).astype(int)

def promo_interval_to_int(pi):
    if pd.isna(pi):
        return 0
    return len(pi.split(','))

grouped['PromoInterval'] = grouped['PromoInterval'].apply(promo_interval_to_int).astype(int)

grouped['StoreType'] = grouped['StoreType'].map({'a': 0, 'b': 1, 'c': 2, 'd': 3}).fillna(-1).astype(int)

# Prepare final result with exact target schema and types
result = pd.DataFrame()
result['StoreType'] = grouped['StoreType']
result['Store'] = grouped['Store'].astype(int)
result['Dept'] = grouped['Dept'].astype(int)
result['Weekly_Sales'] = grouped['Weekly_Sales'].round().astype(int)
result['IsHoliday'] = grouped['IsHoliday'].astype(int)
result['Assortment'] = grouped['Assortment']
result['CompetitionDistance'] = grouped['CompetitionDistance']
result['CompetitionOpenSinceMonth'] = grouped['CompetitionOpenSinceMonth']
result['CompetitionOpenSinceYear'] = grouped['CompetitionOpenSinceYear']
result['Promo2'] = grouped['Promo2']
result['Promo2SinceWeek'] = grouped['Promo2SinceWeek']
result['Promo2SinceYear'] = grouped['Promo2SinceYear']
result['PromoInterval'] = grouped['PromoInterval']

result.to_csv(target_path, index=False)