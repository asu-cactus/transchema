import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_53/training_0.csv", index_col=0)

melted = df0.melt(id_vars=["continent"], value_vars=["beer_servings", "spirit_servings", "wine_servings", "total_litres_of_pure_alcohol"], var_name="variable", value_name="value")

pivoted = melted.pivot_table(index="continent", columns="variable", values="value", aggfunc="mean").reset_index()

pivoted = pivoted.rename_axis(None, axis=1)

pivoted = pivoted[["continent", "beer_servings", "spirit_servings", "wine_servings", "total_litres_of_pure_alcohol"]]

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length1_53/target_multisource_mcts.csv", index=False)