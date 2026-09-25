import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_88/training_0.csv", index_col=0)

# Group by all columns except Price, aggregate Price by mean
group_cols = ['Airline', 'Date_of_Journey', 'Source', 'Destination', 'Route', 'Dep_Time', 'Arrival_Time', 'Duration', 'Total_Stops', 'Additional_Info']

df_grouped = df0.groupby(group_cols, as_index=False).agg({'Price': 'mean'})

# Convert Price to int as in target schema
df_grouped['Price'] = df_grouped['Price'].round().astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_88/target_multisource_mcts.csv", index=False)