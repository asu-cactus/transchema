import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_88/training_0.csv", index_col=0)

df0['Price'] = pd.to_numeric(df0['Price'], errors='coerce').fillna(0).astype(int)
df0 = df0.astype({
    'Airline': 'string',
    'Date_of_Journey': 'string',
    'Source': 'string',
    'Destination': 'string',
    'Route': 'string',
    'Dep_Time': 'string',
    'Arrival_Time': 'string',
    'Duration': 'string',
    'Total_Stops': 'string',
    'Additional_Info': 'string',
})

df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_88/target_multisource_mcts.csv", index=False)