import pandas as pd
import numpy as np

source0_path = "autopipeline-benchmarks/github-pipelines/length2_28/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_28/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_28/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

df1['IsHoliday'] = df1['IsHoliday'].astype(int)
df0['Assortment'] = df0['Assortment'].astype('category').cat.codes

merged = pd.merge(df1, df0, on='Store', how='inner', suffixes=('_1', '_0'))

grouped = merged.groupby(
    ['StoreType', 'Store', 'Dept', 'IsHoliday', 'Assortment'],
    dropna=False,
    as_index=False
).agg(
    Weekly_Sales=('Weekly_Sales', 'sum'),
    Dept_count=('Dept', 'count'),
    CompetitionDistance_max=('CompetitionDistance', 'max'),
    CompetitionDistance_min=('CompetitionDistance', 'min'),
    CompetitionOpenSinceMonth_max=('CompetitionOpenSinceMonth', 'max'),
    CompetitionOpenSinceYear_max=('CompetitionOpenSinceYear', 'max'),
    Promo2_max=('Promo2', 'max'),
    Promo2SinceWeek_max=('Promo2SinceWeek', 'max'),
    Promo2SinceYear_max=('Promo2SinceYear', 'max'),
    PromoInterval_max=('PromoInterval', 'max')
)

# According to target schema:
# 'StoreType': string
# 'Store': integer
# 'Dept': integer
# 'Weekly_Sales': integer
# 'IsHoliday': integer
# 'Assortment': integer
# 'CompetitionDistance': integer
# 'CompetitionOpenSinceMonth': integer
# 'CompetitionOpenSinceYear': integer
# 'Promo2': integer
# 'Promo2SinceWeek': integer
# 'Promo2SinceYear': integer
# 'PromoInterval': integer

# Use CompetitionDistance_min as CompetitionDistance (min and max differ, choose min as in plan)
# Drop Dept_count (not in target)
# Rename columns accordingly

result = pd.DataFrame()
result['StoreType'] = grouped['StoreType'].astype(str)
result['Store'] = grouped['Store'].astype(int)
result['Dept'] = grouped['Dept'].astype(int)
result['Weekly_Sales'] = grouped['Weekly_Sales'].round().astype(int)
result['IsHoliday'] = grouped['IsHoliday'].astype(int)
result['Assortment'] = grouped['Assortment'].astype(int)
result['CompetitionDistance'] = grouped['CompetitionDistance_min'].round().astype('Int64')
result['CompetitionOpenSinceMonth'] = grouped['CompetitionOpenSinceMonth_max'].round().astype('Int64')
result['CompetitionOpenSinceYear'] = grouped['CompetitionOpenSinceYear_max'].round().astype('Int64')
result['Promo2'] = grouped['Promo2_max'].round().astype('Int64')
result['Promo2SinceWeek'] = grouped['Promo2SinceWeek_max'].round().astype('Int64')
result['Promo2SinceYear'] = grouped['Promo2SinceYear_max'].round().astype('Int64')

# PromoInterval is string in source but target expects integer, convert PromoInterval strings to integer codes
promo_intervals = grouped['PromoInterval_max'].astype(str)
promo_interval_codes = promo_intervals.astype('category').cat.codes
promo_interval_codes = promo_interval_codes.replace(-1, pd.NA)
result['PromoInterval'] = promo_interval_codes.astype('Int64')

result.to_csv(target_path, index=False)