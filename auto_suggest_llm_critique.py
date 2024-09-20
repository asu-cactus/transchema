# Where to start 
# check if target_multisource is there 
# if yes,
#     then check the accuracy,
#     If the score is 1, then skip 
#     else get the critique prompt 
#         generate new python script based on this critique prompt 

# else 
#     using the operation history, generate the multisource file 
#     then follow the same process as if 

# What to put in critique prompt 
#     Comparision between FD mappings, keys and column mapping information as hint 

#     1. Ask llm to generate the python code that solves the FD mapping issue using a group by, count
    
#     2. Ask llm to find a way to generate the operator that should be used to satisfy FD mappings, if it gives group by, then check the number of the rows generated in the solution.
#         It may not be able to get the generate the count but it should generate the group by.