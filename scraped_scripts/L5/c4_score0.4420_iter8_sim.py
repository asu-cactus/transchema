import pandas as pd

Source5_4_0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_0.csv", index_col=0)
Source5_4_1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_1.csv", index_col=0)
Source5_4_2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_2.csv", index_col=0)
Source5_4_3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_3.csv", index_col=0)

joined_0_3 = pd.merge(Source5_4_0, Source5_4_3, on="Artist", how="left")

union_result = pd.concat([joined_0_3, Source5_4_2], ignore_index=True, sort=False)

final_join = pd.merge(union_result, Source5_4_1, on="Artist", how="left")

final = final_join[[
    "Artist",
    "Year Inducted",
    "Years Waited",
    "# of Years Nominated",
    "Inducted By",
    "Influenced",
    "Certified Units (Millions)"
]]

final["Year Inducted"] = pd.to_numeric(final["Year Inducted"], errors='coerce')
final["Years Waited"] = pd.to_numeric(final["Years Waited"], errors='coerce').astype('Int64')
final["# of Years Nominated"] = pd.to_numeric(final["# of Years Nominated"], errors='coerce').astype('Int64')
final["Influenced"] = pd.to_numeric(final["Influenced"], errors='coerce').astype('Int64')
final["Certified Units (Millions)"] = pd.to_numeric(final["Certified Units (Millions)"], errors='coerce')

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_4/target_multisource_mcts.csv", index=False)