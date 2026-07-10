import pandas as pd

# Read source files with index_col=0 to ignore the first index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_28/training_1.csv", index_col=0)

# Join on 'Store'
df = pd.merge(df1, df0, on="Store", how="inner")

# Define aggregation dictionary
agg_dict = {
    "Dept": "sum",
    "Weekly_Sales": "sum",
    "IsHoliday": lambda x: x.astype(int).sum(),
    "Assortment": "first",
    "CompetitionDistance": "sum",
    "CompetitionOpenSinceMonth": "sum",
    "CompetitionOpenSinceYear": "sum",
    "Promo2": "sum",
    "Promo2SinceWeek": "sum",
    "Promo2SinceYear": "sum",
    "PromoInterval": "first"
}

# Group by StoreType and Store
df_grouped = df.groupby(["StoreType", "Store"], as_index=False).agg(agg_dict)

# Convert boolean IsHoliday to int explicitly (already done in aggregation)
df_grouped["IsHoliday"] = df_grouped["IsHoliday"].astype(int)

# Write output with exact target schema column order
target_columns = ['StoreType', 'Store', 'Dept', 'Weekly_Sales', 'IsHoliday', 'Assortment',
                  'CompetitionDistance', 'CompetitionOpenSinceMonth', 'CompetitionOpenSinceYear',
                  'Promo2', 'Promo2SinceWeek', 'Promo2SinceYear', 'PromoInterval']

df_grouped = df_grouped[target_columns]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_28/target_multisource_mcts.csv", index=False)