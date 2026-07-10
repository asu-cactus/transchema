import pandas as pd

s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_3.csv", index_col=0)
join_result = pd.merge(s2, s3, left_on="addr_state", right_on="addr_state", suffixes=('_2', '_3'))

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_0.csv", index_col=0)
join_result = pd.merge(join_result, s0, left_on="addr_state", right_on="addr_state", suffixes=('', '_0'))

s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_1.csv", index_col=0)
join_result = pd.merge(join_result, s1, left_on="addr_state", right_on="addr_state", suffixes=('', '_1'))

s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_4.csv", index_col=0)
join_result = pd.merge(join_result, s4, left_on="addr_state", right_on="addr_state", suffixes=('', '_4'))

s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_5.csv", index_col=0)
join_result = pd.merge(join_result, s5, left_on="addr_state", right_on="addr_state", suffixes=('', '_5'))

s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_6.csv", index_col=0)
join_result = pd.merge(join_result, s6, left_on="addr_state", right_on="addr_state", suffixes=('', '_6'))

s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_7.csv", index_col=0)
join_result = pd.merge(join_result, s7, left_on="addr_state", right_on="addr_state", suffixes=('', '_7'))

s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_8.csv", index_col=0)
join_result = pd.merge(join_result, s8, left_on="addr_state", right_on="addr_state", suffixes=('', '_8'))

s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_9.csv", index_col=0)
join_result = pd.merge(join_result, s9, left_on="addr_state", right_on="addr_state", suffixes=('', '_9'))

s10 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_10.csv", index_col=0)
join_result = pd.merge(join_result, s10, left_on="addr_state", right_on="addr_state", suffixes=('', '_10'))

s11 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_11.csv", index_col=0)
join_result = pd.merge(join_result, s11, left_on="addr_state", right_on="addr_state", suffixes=('', '_11'))

s12 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_12.csv", index_col=0)
join_result = pd.merge(join_result, s12, left_on="addr_state", right_on="addr_state", suffixes=('', '_12'))

s13 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_13.csv", index_col=0)
join_result = pd.merge(join_result, s13, left_on="addr_state", right_on="addr_state", suffixes=('', '_13'))

s14 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_53/training_14.csv", index_col=0)
join_result = pd.merge(join_result, s14, left_on="addr_state", right_on="addr_state", suffixes=('', '_14'))

pivot_df = join_result.copy()
pivot_df.columns = [col if col == "addr_state" else f"addr_state_{i}" for i, col in enumerate(pivot_df.columns)]
pivot_df = pivot_df.drop(columns=["addr_state_0"]) if "addr_state_0" in pivot_df.columns else pivot_df

pivot_df = pivot_df.melt(id_vars=["addr_state"], value_vars=[c for c in pivot_df.columns if c != "addr_state"], value_name="addr_state_val")
pivot_df = pivot_df.drop(columns=["variable"])
pivot_df = pivot_df.rename(columns={"addr_state_val": "addr_state"})
pivot_df = pivot_df.astype({"addr_state": "Int64"})

pivot_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_53/target_multisource_mcts.csv", index=False)