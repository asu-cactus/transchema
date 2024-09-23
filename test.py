import pandas as pd
from quality.quality import analyze_functional_dependencies,data_profiling,data_summary
from valentine import valentine_match
import valentine.algorithms as algorithms

def calculate_score(gt_df, tgt_df) :
    # Match Functional Dependencies 
    fd_gt, key_gt = analyze_functional_dependencies(gt_df)
    fd_tgt, key_tgt = analyze_functional_dependencies(tgt_df)

    print(fd_gt)
    print(key_gt)

    total_fds = len(fd_gt)
    total_keys = len(key_gt)
    
    discovered_fd = 0
    for fd in fd_gt : 
        if(fd in fd_tgt) : 
            print(fd)
            discovered_fd += 1

    fd_score = discovered_fd/total_fds

    discovered_keys = 0
    for key in key_gt : 
        if key in key_tgt : 
            print(key)
            discovered_keys += 1

    key_score = discovered_keys / total_keys
    
    # df_gt_schema = {col: gt_df[col].dtype for col in gt_df.columns}
    # df_tgt_schema = {col: tgt_df[col].dtype for col in tgt_df.columns}

    matcher = algorithms.Cupid()

    # Match schemas
    matches = valentine_match(gt_df, tgt_df,matcher)
    gt_df_columns = gt_df.columns

    gt_df_columns = set(gt_df.columns)
    matched_columns = set(match[0] for match in matches)
    
    column_mapping_score = len(matched_columns) / len(gt_df_columns)
    

    return [fd_score, key_score, column_mapping_score]


    # Match keys 

    # Match column mappings  

gt_path = "autopipeline-benchmarks/github-pipelines/length4_28/target.csv"
tgt_path = "autopipeline-benchmarks/github-pipelines/length4_28/target_multisource_recovered.csv"

gt_df = pd.read_csv(gt_path)
tgt_df = pd.read_csv(tgt_path)

try : 
    gt_df = gt_df.drop('Unnamed: 0', axis=1)
except : 
    pass
try : 
    tgt_df = tgt_df.drop('Unnamed: 0', axis=1)
except : 
    pass
key_gt,fd_gt = analyze_functional_dependencies(gt_df)
key_tgt, fd_tgt = analyze_functional_dependencies(tgt_df)


# # print(gt_df, tgt_df)
# print("Ground Truth : ")
# print(key_gt, fd_gt)
# print(" Generated table : ")
# print(key_tgt, fd_tgt)

single_analysis, multi_analysis, dependencies = data_profiling(gt_df)

y = data_summary(single_analysis, multi_analysis, dependencies)

print('\n\n\nSummary : ')
print(y)

print(calculate_score(gt_df,tgt_df))