import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_4.csv", index_col=0)

# PIVOT and GROUP_BY on Customer_Segment: 
# We need to get Customer_Segment per Ord_id from s1 and s4.
# s4 has Ord_id, Cust_id, Prod_id, Ship_id
# s1 has Cust_id and Customer_Segment
# So first join s4 and s1 on Cust_id to get Customer_Segment per Ord_id
joined_41 = pd.merge(s4, s1[['Cust_id', 'Customer_Segment']], on='Cust_id', how='left')

# Now group by Customer_Segment and Ord_id, Prod_id, Ship_id, Cust_id to get unique rows
# The target schema is ['Customer_Segment', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']
# The example shows all columns have the same values per row, so no aggregation needed, just drop duplicates
result = joined_41[['Customer_Segment', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']].drop_duplicates()

# Convert Ord_id, Prod_id, Ship_id, Cust_id to integer-like by extracting numeric part
def to_int_id(x):
    if pd.isna(x):
        return x
    return int(''.join(filter(str.isdigit, str(x))))

result['Ord_id'] = result['Ord_id'].map(to_int_id)
result['Prod_id'] = result['Prod_id'].map(to_int_id)
result['Ship_id'] = result['Ship_id'].map(to_int_id)
result['Cust_id'] = result['Cust_id'].map(to_int_id)

result = result[['Customer_Segment', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_44/target_multisource_mcts.csv", index=False)