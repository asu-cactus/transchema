import pandas as pd

# Read source CSV
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_45/training_0.csv", index_col=0)

# Group by Gender and aggregate
agg_df = df0.groupby("Gender").agg(
    Purchase_Count=("Purchase ID", "count"),
    SN=("SN", pd.Series.nunique),
    Age_x=("Age", pd.Series.nunique),
    Item_ID_x=("Item ID", pd.Series.nunique),
    Item_Name=("Item Name", pd.Series.nunique),
    Price=("Price", pd.Series.nunique),
    Purchase_ID_x=("Purchase ID", "sum"),
    Age_y=("Age", "sum"),
    Item_ID_y=("Item ID", "sum"),
    Average_Purchase_Price=("Price", "mean"),
    Purchase_ID_y=("Purchase ID", "count"),
    Age=("Age", "mean"),
    Item_ID=("Item ID", "mean"),
    Total_Purchase_Value=("Price", "sum"),
).reset_index()

# Rename columns to match target schema exactly
agg_df = agg_df.rename(columns={
    "Purchase_Count": "Purchase Count",
    "SN": "SN",
    "Age_x": "Age_x",
    "Item_ID_x": "Item ID_x",
    "Item_Name": "Item Name",
    "Price": "Price",
    "Purchase_ID_x": "Purchase ID_x",
    "Age_y": "Age_y",
    "Item_ID_y": "Item ID_y",
    "Average_Purchase_Price": "Average Purchase Price",
    "Purchase_ID_y": "Purchase ID_y",
    "Age": "Age",
    "Item_ID": "Item ID",
    "Total_Purchase_Value": "Total Purchase Value",
})

# Ensure correct dtypes as per target schema
agg_df["Purchase Count"] = agg_df["Purchase Count"].astype(int)
agg_df["SN"] = agg_df["SN"].astype(int)
agg_df["Age_x"] = agg_df["Age_x"].astype(int)
agg_df["Item ID_x"] = agg_df["Item ID_x"].astype(int)
agg_df["Item Name"] = agg_df["Item Name"].astype(int)
agg_df["Price"] = agg_df["Price"].astype(int)
agg_df["Purchase ID_x"] = agg_df["Purchase ID_x"].astype(float)
agg_df["Age_y"] = agg_df["Age_y"].astype(float)
agg_df["Item ID_y"] = agg_df["Item ID_y"].astype(float)
agg_df["Average Purchase Price"] = agg_df["Average Purchase Price"].astype(float)
agg_df["Purchase ID_y"] = agg_df["Purchase ID_y"].astype(int)
agg_df["Age"] = agg_df["Age"].astype(int)
agg_df["Item ID"] = agg_df["Item ID"].astype(int)
agg_df["Total Purchase Value"] = agg_df["Total Purchase Value"].astype(float)

# Reorder columns to match target schema
final_cols = ['Gender', 'Purchase Count', 'SN', 'Age_x', 'Item ID_x', 'Item Name', 'Price',
              'Purchase ID_x', 'Age_y', 'Item ID_y', 'Average Purchase Price', 'Purchase ID_y',
              'Age', 'Item ID', 'Total Purchase Value']

result = agg_df[final_cols]

# Write to CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_45/target_multisource_mcts.csv", index=False)