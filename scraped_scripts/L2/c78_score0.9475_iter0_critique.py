import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_78/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_78/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_78/training_2.csv", index_col=0)

# Join Source0 and Source1 on Prod_id
join1 = pd.merge(source0, source1, on="Prod_id", how="inner")

# Join the above result with Source2 on Cust_id
join2 = pd.merge(join1, source2, on="Cust_id", how="inner")

# Define group by keys (leftmost string columns that uniquely identify rows)
group_keys = ['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']

# Aggregation columns (all other columns)
agg_cols = ['Sales', 'Discount', 'Order_Quantity', 'Profit', 'Shipping_Cost', 'Product_Base_Margin',
            'Product_Category', 'Product_Sub_Category', 'Customer_Name', 'Province', 'Region', 'Customer_Segment']

# Aggregate by taking the first value in each group (to remove duplicates)
agg_dict = {col: 'first' for col in agg_cols}

target = join2.groupby(group_keys, as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
target_columns = ['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount', 'Order_Quantity', 'Profit',
                  'Shipping_Cost', 'Product_Base_Margin', 'Product_Category', 'Product_Sub_Category',
                  'Customer_Name', 'Province', 'Region', 'Customer_Segment']

target = target[target_columns]

target.to_csv("autopipeline-benchmarks/github-pipelines/length2_78/target_multisource_mcts.csv", index=False)