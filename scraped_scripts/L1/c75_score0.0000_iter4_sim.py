import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_75/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on="host_id", suffixes=("", "_y"))

grouped = joined.groupby("neighbourhood", as_index=False).agg({
    "id": "max",
    "name": "max",
    "host_id": "max",
    "host_name": "max",
    "neighbourhood_group": "max",
    "latitude": "max",
    "longitude": "max",
    "room_type": "max",
    "price": "max",
    "minimum_nights": "max",
    "number_of_reviews": "max",
    "last_review": "max",
    "reviews_per_month": "max",
    "calculated_host_listings_count": "max",
    "availability_365": "max"
})

# Convert columns to required types
grouped["neighbourhood"] = grouped["neighbourhood"].astype(str)
int_cols = ['id', 'name', 'host_id', 'host_name', 'neighbourhood_group', 'latitude', 'longitude', 'room_type', 'price', 'minimum_nights', 'number_of_reviews', 'last_review', 'reviews_per_month', 'calculated_host_listings_count', 'availability_365']

for col in int_cols:
    # Convert to numeric, coerce errors to NaN, then fill NaN with 0 and convert to int
    grouped[col] = pd.to_numeric(grouped[col], errors='coerce').fillna(0).astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_75/target_multisource_mcts.csv", index=False)