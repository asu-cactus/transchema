import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_28/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_28/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_28/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

df1['IsHoliday'] = df1['IsHoliday'].astype(int)
agg = df1.groupby(['Store', 'Dept', 'IsHoliday'], as_index=False).agg(
    Weekly_Sales=('Weekly_Sales', 'sum'),
    Date_Count=('Date', 'count')
)

merged = pd.merge(agg, df0, on='Store', how='inner')

merged['IsHoliday'] = merged['IsHoliday'].astype(int)
merged['Assortment'] = merged['Assortment'].map({'a': 0, 'b': 1, 'c': 2}).fillna(-1).astype(int)
merged['Promo2'] = merged['Promo2'].astype(int)
merged['Promo2SinceWeek'] = merged['Promo2SinceWeek'].fillna(0).astype(int)
merged['Promo2SinceYear'] = merged['Promo2SinceYear'].fillna(0).astype(int)
merged['CompetitionDistance'] = merged['CompetitionDistance'].fillna(0).astype(int)
merged['CompetitionOpenSinceMonth'] = merged['CompetitionOpenSinceMonth'].fillna(0).astype(int)
merged['CompetitionOpenSinceYear'] = merged['CompetitionOpenSinceYear'].fillna(0).astype(int)

def promo_interval_to_int(pi):
    if pd.isna(pi):
        return 0
    return len(pi.split(','))

merged['PromoInterval'] = merged['PromoInterval'].apply(promo_interval_to_int).astype(int)

merged['StoreType'] = merged['StoreType'].map({'a': 0, 'b': 1, 'c': 2, 'd': 3}).fillna(-1).astype(int)

result = pd.DataFrame()
result['StoreType'] = merged['StoreType']
result['Store'] = merged['Store'].astype(int)
result['Dept'] = merged['Dept'].astype(int)
result['Weekly_Sales'] = merged['Weekly_Sales'].round().astype(int)
result['IsHoliday'] = merged['IsHoliday'].astype(int)
result['Assortment'] = merged['Assortment']
result['CompetitionDistance'] = merged['CompetitionDistance']
result['CompetitionOpenSinceMonth'] = merged['CompetitionOpenSinceMonth']
result['CompetitionOpenSinceYear'] = merged['CompetitionOpenSinceYear']
result['Promo2'] = merged['Promo2']
result['Promo2SinceWeek'] = merged['Promo2SinceWeek']
result['Promo2SinceYear'] = merged['Promo2SinceYear']
result['PromoInterval'] = merged['PromoInterval']

result.to_csv(target_path, index=False)