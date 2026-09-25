import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_75/training_0.csv", index_col=0)

grouped = df.groupby("neighbourhood").agg({
    "id": "count",
    "name": "count",
    "host_id": "count",
    "host_name": "count",
    "neighbourhood_group": "count",
    "latitude": "count",
    "longitude": "count",
    "room_type": "count",
    "price": "count",
    "minimum_nights": "count",
    "number_of_reviews": "count",
    "last_review": "count",
    "reviews_per_month": "count",
    "calculated_host_listings_count": "count",
    "availability_365": "count"
}).reset_index()

grouped = grouped.rename(columns={
    "id": "id",
    "name": "name",
    "host_id": "host_id",
    "host_name": "host_name",
    "neighbourhood_group": "neighbourhood_group",
    "latitude": "latitude",
    "longitude": "longitude",
    "room_type": "room_type",
    "price": "price",
    "minimum_nights": "minimum_nights",
    "number_of_reviews": "number_of_reviews",
    "last_review": "last_review",
    "reviews_per_month": "reviews_per_month",
    "calculated_host_listings_count": "calculated_host_listings_count",
    "availability_365": "availability_365"
})

for col in grouped.columns:
    if col != "neighbourhood":
        grouped[col] = grouped[col].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_75/target_multisource_mcts.csv", index=False)