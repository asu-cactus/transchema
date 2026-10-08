import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_28/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_28/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_28/target_multisource_mcts.csv"

# Read sources with index_col=0 to ignore first column
df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Convert IsHoliday to int
df1['IsHoliday'] = df1['IsHoliday'].astype(int)

# Convert Assortment to categorical codes (integer)
df0['Assortment'] = df0['Assortment'].astype('category').cat.codes

# Inner join on Store
merged = pd.merge(df1, df0, on='Store', how='inner')

# Group by StoreType, Store, Dept
grouped = merged.groupby(
    ['StoreType', 'Store', 'Dept'],
    dropna=False,
    as_index=False
).agg(
    Weekly_Sales=('Weekly_Sales', 'sum'),
    IsHoliday=('IsHoliday', 'max'),
    Assortment=('Assortment', 'max'),
    CompetitionDistance=('CompetitionDistance', 'min'),
    CompetitionOpenSinceMonth=('CompetitionOpenSinceMonth', 'max'),
    CompetitionOpenSinceYear=('CompetitionOpenSinceYear', 'max'),
    Promo2=('Promo2', 'max'),
    Promo2SinceWeek=('Promo2SinceWeek', 'max'),
    Promo2SinceYear=('Promo2SinceYear', 'max'),
    PromoInterval=('PromoInterval', 'max')
)

# Convert types according to target schema
result = pd.DataFrame()
result['StoreType'] = grouped['StoreType'].astype(str)
result['Store'] = grouped['Store'].astype(int)
result['Dept'] = grouped['Dept'].astype(int)
result['Weekly_Sales'] = grouped['Weekly_Sales'].round().astype(int)
result['IsHoliday'] = grouped['IsHoliday'].astype(int)
result['Assortment'] = grouped['Assortment'].astype(int)
result['CompetitionDistance'] = grouped['CompetitionDistance'].round().astype('Int64')
result['CompetitionOpenSinceMonth'] = grouped['CompetitionOpenSinceMonth'].round().astype('Int64')
result['CompetitionOpenSinceYear'] = grouped['CompetitionOpenSinceYear'].round().astype('Int64')
result['Promo2'] = grouped['Promo2'].round().astype('Int64')
result['Promo2SinceWeek'] = grouped['Promo2SinceWeek'].round().astype('Int64')
result['Promo2SinceYear'] = grouped['Promo2SinceYear'].round().astype('Int64')

# Convert PromoInterval string to categorical codes, preserving NaNs
promo_intervals = grouped['PromoInterval'].astype(str)
promo_interval_codes = promo_intervals.astype('category').cat.codes
promo_interval_codes = promo_interval_codes.replace(-1, pd.NA)
result['PromoInterval'] = promo_interval_codes.astype('Int64')

result.to_csv(target_path, index=False)