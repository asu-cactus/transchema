import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_60/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_60/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_60/training_2.csv", index_col=0)

# Join Source1 and Source2 on Prod_id
join_1 = pd.merge(source1, source2, on="Prod_id", how="inner")

# Join the above with Source0 on Cust_id
join_2 = pd.merge(join_1, source0, on="Cust_id", how="inner")

# Define group by keys (leftmost columns of target schema)
group_by_cols = ['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']

# Aggregations:
# Sum for quantities and amounts
# Mean for discount and product base margin (rates)
# For string columns, take first value (assumed functionally dependent)

agg_dict = {
    'Sales': 'sum',
    'Discount': 'mean',
    'Order_Quantity': 'sum',
    'Profit': 'sum',
    'Shipping_Cost': 'sum',
    'Product_Base_Margin': 'mean',
    'Product_Category': 'first',
    'Product_Sub_Category': 'first',
    'Customer_Name': 'first',
    'Province': 'first',
    'Region': 'first',
    'Customer_Segment': 'first'
}

result = join_2.groupby(group_by_cols, as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
target_columns = ['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount', 'Order_Quantity', 'Profit', 
                  'Shipping_Cost', 'Product_Base_Margin', 'Product_Category', 'Product_Sub_Category', 
                  'Customer_Name', 'Province', 'Region', 'Customer_Segment']

result = result[target_columns]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_60/target_multisource_mcts.csv", index=False)