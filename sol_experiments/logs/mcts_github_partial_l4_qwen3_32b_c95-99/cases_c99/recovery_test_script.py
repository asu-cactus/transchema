import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_99/test_0.csv", index_col=0)
mean_fare = df['Fare'].mean()
median_fare = df['Fare'].median()
df['Fare_x'] = mean_fare
df['Fare_y'] = median_fare
df.to_csv("autopipeline-benchmarks/github-pipelines/length4_99/target_multisource_mcts_recovery_test_val.csv")