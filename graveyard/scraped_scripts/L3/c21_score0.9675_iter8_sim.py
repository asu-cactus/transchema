import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_21/training_0.csv", index_col=0)

agg = df0.groupby("Country").agg(
    AverageTemperature_x=pd.NamedAgg(column="AverageTemperature", aggfunc="min"),
    AverageTemperature_y=pd.NamedAgg(column="AverageTemperature", aggfunc="max"),
).reset_index()

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_21/target_multisource_mcts.csv", index=False)