import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_53/training_0.csv", index_col=0)

# Rename Age to Age Category
df = df.rename(columns={"Age": "Age Category"})

# Encode categorical columns SN, Gender, Item Name to integers
df["SN"], _ = pd.factorize(df["SN"])
df["Gender"], _ = pd.factorize(df["Gender"])
df["Item Name"], _ = pd.factorize(df["Item Name"])

# Convert Price to integer (round)
df["Price"] = df["Price"].round().astype(int)

# Group by Age Category, Purchase ID, SN
grouped = df.groupby(["Age Category", "Purchase ID", "SN"], as_index=False).agg(
    Purchase_Count=("Purchase ID", "count"),
    Total_Purchase_Value=("Price", "sum"),
    Average_Purchase_Price=("Price", "mean"),
)

# Rename columns to match target schema exactly
grouped = grouped.rename(columns={
    "Age Category": "Age Category",
    "Purchase ID": "Purchase ID",
    "SN": "SN",
    "Purchase_Count": "Purchase Count",
    "Total_Purchase_Value": "Total Purchase Value",
    "Average_Purchase_Price": "Average Purchase Price"
})

# Add Gender, Item ID, Item Name, Price columns by taking first value per group (since they are not aggregated)
# We can get these by merging back or by taking first in groupby with agg
# Let's do it by merging the first row per group from original df

first_rows = df.drop_duplicates(subset=["Age Category", "Purchase ID", "SN"])[
    ["Age Category", "Purchase ID", "SN", "Gender", "Item ID", "Item Name", "Price"]
]

# Merge to grouped
result = pd.merge(grouped, first_rows, on=["Age Category", "Purchase ID", "SN"], how="left")

# Reorder columns to match target schema:
# ['Age Category', 'Purchase ID', 'SN', 'Purchase Count', 'Gender', 'Item ID', 'Item Name', 'Price', 'Total Purchase Value', 'Average Purchase Price']

result = result[
    [
        "Age Category",
        "Purchase ID",
        "SN",
        "Purchase Count",
        "Gender",
        "Item ID",
        "Item Name",
        "Price",
        "Total Purchase Value",
        "Average Purchase Price",
    ]
]

# Convert types to match target schema
result["Age Category"] = result["Age Category"].astype(int)
result["Purchase ID"] = result["Purchase ID"].astype(int)
result["SN"] = result["SN"].astype(int)
result["Purchase Count"] = result["Purchase Count"].astype(int)
result["Gender"] = result["Gender"].astype(int)
result["Item ID"] = result["Item ID"].astype(int)
result["Item Name"] = result["Item Name"].astype(int)
result["Price"] = result["Price"].astype(int)
result["Total Purchase Value"] = result["Total Purchase Value"].astype(float)
result["Average Purchase Price"] = result["Average Purchase Price"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_53/target_multisource_mcts.csv", index=False)