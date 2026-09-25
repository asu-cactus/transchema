import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_28/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_28/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_28/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

merged = pd.merge(df0, df1, how='inner', on=['Store'])

result = pd.DataFrame()
result['StoreType'] = merged['StoreType'].astype(str)
result['Store'] = merged['Store'].astype(int)
result['Dept'] = merged['Dept'].astype(int)
result['Weekly_Sales'] = merged['Weekly_Sales'].round().astype(int)
result['IsHoliday'] = merged['IsHoliday'].astype(bool).astype(int)
result['Assortment'] = merged['Assortment'].astype(str).map({'a':0, 'b':1, 'c':2}).fillna(-1).astype(int)
result['CompetitionDistance'] = merged['CompetitionDistance'].fillna(0).astype(int)
result['CompetitionOpenSinceMonth'] = merged['CompetitionOpenSinceMonth'].fillna(0).astype(int)
result['CompetitionOpenSinceYear'] = merged['CompetitionOpenSinceYear'].fillna(0).astype(int)
result['Promo2'] = merged['Promo2'].fillna(0).astype(int)
result['Promo2SinceWeek'] = merged['Promo2SinceWeek'].fillna(0).astype(int)
result['Promo2SinceYear'] = merged['Promo2SinceYear'].fillna(0).astype(int)

def promo_interval_to_int(pi):
    if pd.isna(pi):
        return 0
    mapping = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sept':9, 'Oct':10, 'Nov':11, 'Dec':12}
    months = pi.split(',')
    # Encode as bitmask or sum of month numbers; here sum of month numbers
    return sum(mapping.get(m.strip()[:3],0) for m in months)

result['PromoInterval'] = merged['PromoInterval'].apply(promo_interval_to_int).astype(int)

result.to_csv(target_path, index=False)