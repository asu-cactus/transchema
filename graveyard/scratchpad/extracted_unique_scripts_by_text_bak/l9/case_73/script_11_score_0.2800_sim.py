import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_4.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_5.csv", index_col=0)
src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_6.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_7.csv", index_col=0)
src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_8.csv", index_col=0)
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_9.csv", index_col=0)

join_5_0 = pd.merge(src5, src0, left_on="sampled_bid_id", right_on="bid_id", how="inner")

union_sources = [src0, src1, src2, src3, src4, src6, src7, src8, src9]
union_all = pd.concat(union_sources, ignore_index=True, sort=False)

final_join = pd.merge(union_all, join_5_0[['sampled_bid_id', 'message']], left_on='bid_id', right_on='sampled_bid_id', how='inner')

result = final_join[['bid_id', 'message']].copy()
result['bid_id'] = result['bid_id'].astype('Int64')
result['message'] = result['message'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_73/target_multisource_mcts.csv", index=False)