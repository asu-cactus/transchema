import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_88/training_0.csv", index_col=0)

df0['Price'] = df0['Price'].astype(int)
df0 = df0.astype({
    'Airline': str,
    'Date_of_Journey': str,
    'Source': str,
    'Destination': str,
    'Route': str,
    'Dep_Time': str,
    'Arrival_Time': str,
    'Duration': str,
    'Total_Stops': str,
    'Additional_Info': str
})

df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_88/target_multisource_mcts.csv", index=False)