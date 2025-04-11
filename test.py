import pandas as pd
from quality.quality import analyze_functional_dependencies,data_profiling,data_summary
from valentine import valentine_match
import valentine.algorithms as algorithms
import sys

def compare_fds(dependencies_gt, dependencies_tgt) : 
    overlapping_dependencies = dependencies_gt.intersection(dependencies_tgt)
    unfounded_dependencies = dependencies_gt - overlapping_dependencies
    print(unfounded_dependencies)

def extract_dependencies(fd_dict):
    dependencies = set()  # Use a set to avoid duplicates
    for determinant, dependents in fd_dict.items():
        for dependent in dependents:
            dependencies.add((determinant, dependent))
    return dependencies

def calculate_score(gt_df, tgt_df) :

    #parameters 
    w1 = 1
    w2 = 1
    w3 = 1
    p  = 1

    # Match Functional Dependencies 
    key_gt, fd_gt = get_filtered_functional_dependency(gt_df)
    key_tgt, fd_tgt = get_filtered_functional_dependency(tgt_df)

    print("\n\n\nScore Calculation\n\n\n")

    print(fd_gt)
    print(key_gt)
    print("\n\nTarget : ")
    print(fd_tgt)
    print(key_tgt)

    dependencies_gt = extract_dependencies(fd_gt)
    dependencies_tgt = extract_dependencies(fd_tgt)

    overlapping_dependencies = dependencies_gt.intersection(dependencies_tgt)
    overlapping_keys = set(key_gt).intersection(key_tgt)

    score_fd = len(overlapping_dependencies)/len(dependencies_gt) if (len(dependencies_gt)>0) else 1
    score_key = len(overlapping_keys) / len(key_gt) if (len(key_gt)>0) else 1

    matcher = algorithms.Cupid()

    # Match schemas
    matches = valentine_match(gt_df, tgt_df,matcher)
    gt_df_columns = gt_df.columns

    gt_df_columns = set(gt_df.columns)
    matched_columns = set(match[0] for match in matches)
    # print("\n\n Matchings : ", matches)
    
    column_mapping_score = len(matched_columns) / len(gt_df_columns)

    score = pow( w1*(score_fd**p) + w2*(score_key**p) + w3*(column_mapping_score)**p ,1/p)

    print([score_fd, score_key, column_mapping_score])
    return score


    # Match keys 

    # Match column mappings  

def get_filtered_functional_dependency(df) :

    # take only first 15 columns and 1000 rows to analyse functional dependencies 
    df = df.sample(n = min(1000,df.shape[0]), replace = False)
    df = df.iloc[:, : 15]

    

    filtered_F, all_keys_sorted = analyze_functional_dependencies(df)

    if not filtered_F or not all_keys_sorted:
        return [],{}

    # Find the key with the most dependencies
    key_dependencies = {}
    for key, value in filtered_F:
        key = key[0]  # Assuming key is always a single-element tuple
        if key not in key_dependencies:
            key_dependencies[key] = set()
        key_dependencies[key].add(value)

    # Sort keys by number of dependencies, descending
    sorted_keys = sorted(key_dependencies.keys(), key=lambda k: len(key_dependencies[k]), reverse=True)

    # filter key based on rules 
    # If key is first and numerical, it can be a key
    # If key is string type, it can be a key 
    sorted_filtered_keys = []
    for key in sorted_keys : 
        if( df.columns.get_loc(key) == 0 ) : 
            sorted_filtered_keys.append(key)
        elif( df[key].dtype == "object" ) : 
            sorted_filtered_keys.append(key)
    filtered_fd = {key: key_dependencies[key] for key in sorted_filtered_keys if key in key_dependencies}
    
    print("\n\n",sorted_filtered_keys)
    print(filtered_fd)

    return sorted_filtered_keys, filtered_fd

    
def get_fd_hints(keys,fds) :
    if not keys : 
        return "No Clear Functional Dependencies Found" 
    
    hint = "Functional Dependencies discovered : \n"
    for key in keys : 
        hint += "Functional Dependencies Associated with key " + key + " : "
        for v in fds[key] : 
            hint += key + " -> " + v + " , "
        hint += "\n"
    if(hint == "Functional Dependencies discovered : \n") : 
        return ""
    else :
        return hint 
    
# if not sorted_filtered_keys:
    #     return "No clear functional dependencies found"

    # hint = "Functional Dependencies discovered : \n"
    # for key in sorted_filtered_keys : 
    #     hint += "Functional Dependencies Associated with key " + key + " : "
    #     for v in key_dependencies[key] : 
    #         hint += key + " -> " + v + " , "
    #     hint += "\n"
    # if(hint == "Functional Dependencies discovered : \n") : 
    #     return ""
    # else :
    #     return hint 

gt_path = "autopipeline-benchmarks/github-pipelines/length2_13/target.csv"
tgt_path = "autopipeline-benchmarks/github-pipelines/length2_13/target_multisource_bayesian_training.csv"

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
# key_gt,fd_gt = analyze_functional_dependencies(gt_df)
gt_df = gt_df.sample(n = min(1000,gt_df.shape[0]), replace = False)
gt_df = gt_df.iloc[:, : 15]
tgt_df = tgt_df.sample(n = min(1000,tgt_df.shape[0]), replace = False)
tgt_df = tgt_df.iloc[:, : 15]
#filter hints based on feature set
# Feature 
# [0.1, 0.1, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0]
# print(gt_df,tgt_df)

# sys.exit()

# a,b = get_filtered_functional_dependency(gt_df)
# 

score = calculate_score(gt_df,tgt_df)
print(score)
# fd_gt = extract_dependencies(a)
# fd_tgt = extract_dependencies(b)

# unf = compare_fds(fd_gt, fd_tgt)

# print(unf)



    
