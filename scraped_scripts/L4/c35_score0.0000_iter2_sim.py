import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_4.csv", index_col=0)

j1 = pd.merge(s4, s1, on="batsman", how="inner", suffixes=('_4', '_1'))
j2 = pd.merge(j1, s0, on="batsman", how="inner", suffixes=('', '_0'))
j3 = pd.merge(j2, s2, on="batsman", how="inner", suffixes=('', '_2'))
j4 = pd.merge(j3, s3, on="batsman", how="inner", suffixes=('', '_3'))

agg = j4.groupby("batsman").agg(
    batsman_runs_x=pd.NamedAgg(column="batsman_runs_0", aggfunc="sum"),
    batsman_runs_y=pd.NamedAgg(column="batsman_runs_2", aggfunc="sum"),
    no_of_balls=pd.NamedAgg(column="no of balls", aggfunc="sum"),
    batsman_runs_x_4=pd.NamedAgg(column="batsman_runs_4", aggfunc="sum"),
    strike=pd.NamedAgg(column="strike", aggfunc="first"),
    batsman_runs_y_6=pd.NamedAgg(column="batsman_runs_3", aggfunc="sum"),
    total_runs=pd.NamedAgg(column="total_runs", aggfunc="sum"),
).reset_index()

agg = agg.rename(columns={"no_of_balls": "no of balls"})

agg["strike"] = agg["strike"].astype(float)
agg["batsman_runs_x"] = agg["batsman_runs_x"].astype(int)
agg["batsman_runs_y"] = agg["batsman_runs_y"].astype(int)
agg["no of balls"] = agg["no of balls"].astype(int)
agg["batsman_runs_x_4"] = agg["batsman_runs_x_4"].astype(int)
agg["batsman_runs_y_6"] = agg["batsman_runs_y_6"].astype(int)
agg["total_runs"] = agg["total_runs"].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_35/target_multisource_mcts.csv", index=False)