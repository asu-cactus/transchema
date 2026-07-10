import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_23/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_23/training_1.csv", index_col=0)

df1_unpivot = df1.melt(id_vars=["city"], value_vars=["driver_count", "type"], var_name="type", value_name="type_value")

def try_int(x):
    try:
        return int(x)
    except:
        return pd.NA

df1_unpivot["type"] = df1_unpivot["type_value"].apply(try_int)
df1_unpivot.loc[df1_unpivot["type"].isna(), "type"] = df1_unpivot.loc[df1_unpivot["type"].isna(), "type_value"]

df1_unpivot = df1_unpivot[["city", "type"]]

df0_renamed = df0.rename(columns={"fare": "type"})
df0_renamed["type"] = pd.to_numeric(df0_renamed["type"], errors="coerce").fillna(0).astype(int)

df_union = pd.concat([df0_renamed[["city", "type"]], df1_unpivot], ignore_index=True)

df_union["type"] = pd.to_numeric(df_union["type"], errors="coerce").fillna(0).astype(int)

df_union.to_csv("autopipeline-benchmarks/github-pipelines/length2_23/target_multisource_mcts.csv", index=False)