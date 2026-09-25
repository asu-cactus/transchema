import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_88/training_0.csv", index_col=0)

df0['Price'] = pd.to_numeric(df0['Price'], errors='coerce').astype('Int64')

df0 = df0[['Airline', 'Date_of_Journey', 'Source', 'Destination', 'Route', 'Dep_Time', 'Arrival_Time', 'Duration', 'Total_Stops', 'Additional_Info', 'Price']]

df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_88/target_multisource_mcts.csv", index=False)