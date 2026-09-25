import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_88/training_0.csv", index_col=0)

df0['Price'] = df0['Price'].astype(int)

str_cols = df0.select_dtypes(include=['object']).columns
df0[str_cols] = df0[str_cols].apply(lambda x: x.str.strip())

for col in ['Airline', 'Source', 'Destination', 'Additional_Info', 'Total_Stops', 'Route', 'Duration', 'Dep_Time', 'Arrival_Time', 'Date_of_Journey']:
    if col in df0.columns:
        df0[col] = df0[col].str.title()

df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_88/target_multisource_mcts.csv", index=False)