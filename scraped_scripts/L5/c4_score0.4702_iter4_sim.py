import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_3.csv", index_col=0)

join_0_3 = pd.merge(source0, source3, on="Artist", how="outer")
join_0_3_1 = pd.merge(join_0_3, source1, on="Artist", how="outer")
join_all = pd.merge(join_0_3_1, source2, on="Artist", how="outer")

result = join_all[[
    "Artist",
    "Year Inducted_x",  # from source0
    "Years Waited_x",   # from source0
    "# of Years Nominated_x",  # from source0
    "Inducted By",
    "Influenced",
    "Certified Units (Millions)"
]]

result = result.rename(columns={
    "Year Inducted_x": "Year Inducted",
    "Years Waited_x": "Years Waited",
    "# of Years Nominated_x": "# of Years Nominated"
})

result["Year Inducted"] = pd.to_numeric(result["Year Inducted"], errors='coerce')
result["Years Waited"] = pd.to_numeric(result["Years Waited"], errors='coerce').astype('Int64')
result["# of Years Nominated"] = pd.to_numeric(result["# of Years Nominated"], errors='coerce').astype('Int64')
result["Influenced"] = pd.to_numeric(result["Influenced"], errors='coerce').astype('Int64')
result["Certified Units (Millions)"] = pd.to_numeric(result["Certified Units (Millions)"], errors='coerce')

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_4/target_multisource_mcts.csv", index=False)