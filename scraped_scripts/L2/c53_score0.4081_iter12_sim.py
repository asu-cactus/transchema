import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_53/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_53/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_53/training_2.csv", index_col=0)

join_result = pd.merge(source0, source2, on="Athlete", how="inner")

join_result = join_result.rename(columns={"Sport": "Sport", "Country": "Country"})
join_result["Age"] = pd.NA
join_result["Year"] = pd.NA
join_result["Closing Ceremony Date"] = pd.NA
join_result["Gold Medals"] = pd.NA
join_result["Silver Medals"] = pd.NA
join_result["Bronze Medals"] = pd.NA
join_result["Total Medals"] = pd.NA

join_result = join_result[["Athlete", "Age", "Year", "Closing Ceremony Date", "Gold Medals", "Silver Medals", "Bronze Medals", "Total Medals", "Country", "Sport"]]

source1 = source1.copy()
source1["Country"] = pd.NA
source1["Sport"] = pd.NA
source1 = source1[["Athlete", "Age", "Year", "Closing Ceremony Date", "Gold Medals", "Silver Medals", "Bronze Medals", "Total Medals", "Country", "Sport"]]

target = pd.concat([source1, join_result], ignore_index=True)

target["Age"] = pd.to_numeric(target["Age"], errors='coerce')
target["Year"] = pd.to_numeric(target["Year"], errors='coerce', downcast='integer')
target["Gold Medals"] = pd.to_numeric(target["Gold Medals"], errors='coerce', downcast='integer')
target["Silver Medals"] = pd.to_numeric(target["Silver Medals"], errors='coerce', downcast='integer')
target["Bronze Medals"] = pd.to_numeric(target["Bronze Medals"], errors='coerce', downcast='integer')
target["Total Medals"] = pd.to_numeric(target["Total Medals"], errors='coerce', downcast='integer')

target.to_csv("autopipeline-benchmarks/github-pipelines/length2_53/target_multisource_mcts.csv", index=False)