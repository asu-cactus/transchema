import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_61/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_61/training_1.csv", index_col=0)

unpivot = source1.melt(id_vars=["Mouse ID", "Timepoint", "Metastatic Sites"], 
                       value_vars=["Tumor Volume (mm3)"], 
                       var_name="Drug", 
                       value_name="Tumor Volume")
# The unpivot above keeps only one value column, but we want to unpivot by Drug, so we need to rename "Tumor Volume (mm3)" values to Drug names.
# Actually, the source1 has no Drug column, so we must join with source0 to get Drug per Mouse ID.

# Actually, the partial plan says UNPIVOT on source1 on Tumor Volume (mm3) to get Drug column, but source1 has no Drug column.
# So the correct approach is:
# 1) Join source1 with source0 on Mouse ID to get Drug per record.
# 2) Then pivot on Timepoint and Drug to get the target format.

# So let's do the join first:
joined = pd.merge(source1, source0, on="Mouse ID", how="inner")

# Now pivot joined on Timepoint as index, Drug as columns, values as Tumor Volume (mm3)
pivot = joined.pivot_table(index="Timepoint", columns="Drug", values="Tumor Volume (mm3)", aggfunc='first')

# Rename columns to match target schema order
target_cols = ['Capomulin', 'Ceftamin', 'Infubinol', 'Ketapril', 'Naftisol', 'Placebo', 'Propriva', 'Ramicane', 'Stelasyn', 'Zoniferol']
pivot = pivot.reindex(columns=target_cols)

pivot.reset_index(inplace=True)

pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_61/target_multisource_mcts.csv", index=False)