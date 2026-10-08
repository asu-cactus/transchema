import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_45/training_0.csv", index_col=0)

grouped = df0.groupby("Gender").agg(
    Purchase_Count=("Purchase ID", "count"),
    Average_Purchase_Price=("Price", "mean"),
    Total_Purchase_Value=("Price", "sum"),
).reset_index()

grouped["Purchase Count"] = grouped["Purchase_Count"].astype(int)
grouped["Average Purchase Price"] = grouped["Average_Purchase_Price"].astype(float)
grouped["Total Purchase Value"] = grouped["Total_Purchase_Value"].astype(float)

grouped = grouped.rename(columns={"Gender": "Gender"})

# For columns in target schema not present in source or aggregation, fill with NaN or 0 as appropriate
# Target schema: ['Gender': string, 'Purchase Count': integer, 'SN': integer, 'Age_x': integer, 'Item ID_x': integer, 'Item Name': integer, 'Price': integer, 'Purchase ID_x': float, 'Age_y': float, 'Item ID_y': float, 'Average Purchase Price': float, 'Purchase ID_y': integer, 'Age': integer, 'Item ID': integer, 'Total Purchase Value': float]

# Add missing columns with NaN or 0
missing_cols = ['SN', 'Age_x', 'Item ID_x', 'Item Name', 'Price', 'Purchase ID_x', 'Age_y', 'Item ID_y', 'Purchase ID_y', 'Age', 'Item ID']
for col in missing_cols:
    grouped[col] = pd.NA

# Reorder columns to match target schema
final_cols = ['Gender', 'Purchase Count', 'SN', 'Age_x', 'Item ID_x', 'Item Name', 'Price', 'Purchase ID_x', 'Age_y', 'Item ID_y', 'Average Purchase Price', 'Purchase ID_y', 'Age', 'Item ID', 'Total Purchase Value']
result = grouped[final_cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_45/target_multisource_mcts.csv", index=False)