import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_54/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_54/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_54/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_54/training_3.csv", index_col=0)

r0 = pd.merge(df1, df2, on=["CountyID", "CountyName", "Year", "ID"], how="inner", suffixes=('_y', '_x'))
r1 = pd.merge(r0, df0, on=["CountyID", "CountyName", "Year", "ID"], how="inner", suffixes=('_x_10', '_x'))
r2 = pd.merge(r1, df3, on=["CountyID", "CountyName", "Year", "ID"], how="inner", suffixes=('_y_14', '_y'))

result = pd.DataFrame()
result["CountyID_x"] = r2["CountyID"]
result["CountyName_x"] = r2["CountyName"]
result["whites_population"] = r2["whites_population"]
result["Year_x"] = r2["Year"]
result["ID"] = r2["ID"]
result["CountyID_y"] = r2["CountyID"]
result["CountyName_y"] = r2["CountyName"]
result["other_population"] = r2["other_population"]
result["Year_y"] = r2["Year"]
result["CountyID_x_9"] = r2["CountyID"]
result["CountyName_x_10"] = r2["CountyName"]
result["mixed_population"] = r2["mixed_population"]
result["Year_x_12"] = r2["Year"]
result["CountyID_y_13"] = r2["CountyID"]
result["CountyName_y_14"] = r2["CountyName"]
result["black_population"] = r2["black_population"]
result["Year_y_16"] = r2["Year"]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_54/target_multisource_mcts.csv", index=False)