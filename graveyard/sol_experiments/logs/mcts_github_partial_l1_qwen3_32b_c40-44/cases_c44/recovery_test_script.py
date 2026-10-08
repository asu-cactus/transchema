import pandas as pd

df = pd.read_csv(
    "autopipeline-benchmarks/github-pipelines/length1_44/test_0.csv",
    index_col=0
)
result = df.groupby("Country / territory of asylum/residence")["Value"].sum().reset_index()
result.rename(columns={"Value": "Year"}, inplace=True)
result.to_csv(
    "autopipeline-benchmarks/github-pipelines/length1_44/target_multisource_mcts_recovery_test_val.csv",
    index=False
)