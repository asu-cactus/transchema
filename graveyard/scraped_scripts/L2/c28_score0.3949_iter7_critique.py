import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_28/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_28/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_28/target_multisource_mcts.csv"

# Read sources with index_col=0 to ignore the first column (index)
df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Convert IsHoliday to int in df1
df1['IsHoliday'] = df1['IsHoliday'].astype(int)

# Join on 'Store'
merged = pd.merge(df0, df1, on='Store', how='inner')

# Convert StoreType and Assortment to categorical codes
merged['StoreType'] = merged['StoreType'].astype('category').cat.codes
merged['Assortment'] = merged['Assortment'].astype('category').cat.codes

# Convert PromoInterval to categorical codes
merged['PromoInterval'] = merged['PromoInterval'].astype('category').cat.codes

# Convert numeric columns to int, filling NaN with 0
for col in ['CompetitionDistance', 'CompetitionOpenSinceMonth', 'CompetitionOpenSinceYear',
            'Promo2', 'Promo2SinceWeek', 'Promo2SinceYear']:
    merged[col] = pd.to_numeric(merged[col], errors='coerce').fillna(0).astype(int)

# Group by StoreType, Store, Dept, IsHoliday and sum Weekly_Sales
grouped = merged.groupby(['StoreType', 'Store', 'Dept', 'IsHoliday'], as_index=False).agg({'Weekly_Sales': 'sum',
                                                                                        'Assortment': 'first',
                                                                                        'CompetitionDistance': 'first',
                                                                                        'CompetitionOpenSinceMonth': 'first',
                                                                                        'CompetitionOpenSinceYear': 'first',
                                                                                        'Promo2': 'first',
                                                                                        'Promo2SinceWeek': 'first',
                                                                                        'Promo2SinceYear': 'first',
                                                                                        'PromoInterval': 'first'})

# Convert Weekly_Sales to int
grouped['Weekly_Sales'] = grouped['Weekly_Sales'].astype(int)

# Final columns in target schema order
final_cols = ['StoreType', 'Store', 'Dept', 'Weekly_Sales', 'IsHoliday', 'Assortment',
              'CompetitionDistance', 'CompetitionOpenSinceMonth', 'CompetitionOpenSinceYear',
              'Promo2', 'Promo2SinceWeek', 'Promo2SinceYear', 'PromoInterval']

result = grouped[final_cols]

result.to_csv(target_path, index=False)