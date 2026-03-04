from . import binaryRepr
# Create decorator function to see how many times functions are called
def call_counter(func):
    
    def helper(*args, **kwargs):
        helper.calls += 1
        return func(*args, **kwargs);
    helper.calls = 0
    helper.__name__= func.__name__
    return helper;

# Calculate Partition (C_k, r(U)) - the partitions
#                                   of each candidate at level k are calculated
# Takes in data frame of relation and a candidate in C_km1
# Outputs partition of Candidate in C_km1 in relation to data frame

@call_counter
def CardOfPartition(Candidate, df):
    return len(df[Candidate].drop_duplicates())
    # If length is one, find number of unique elements in column
    if len(Candidate) == 1: return df[Candidate[0]].nunique()
    # If length is +1, create groups over which to find number of unique elements
    else:
        dropna_re = df[Candidate].drop_duplicates().count()
        #print("CANDIDATE", Candidate, df.columns, dropna_re, len(dropna_re)) 
        #print(dropna_re.iloc[0])
        return dropna_re.iloc[0] 

# Obtain FDs(C_km1) - checks the FDs of each
#                     candidate X in C_k
#                   - FDs of the form X -> v_i, where
#                     v_i *Exists* U - X^{+} are checked by 
#                     comparing *Partition* X and *Partition* X v_i
#
# F = Null_Set
# for each candidate X in C_km1 
#   for each v_i *exists* U - X^{+}     \\Pruning rule 3
#       if (Cardinality(*Partition* X) == Cardinality(*Partition X v_i)) then
#       {
#           X* = X *Union* {v_i}
#           F = F *Union* {X -> v_i}    \\Theorem 2
#       }
#   return (F);
def get_card(Cardinality, Cand, U, df):
    key = binaryRepr.toBin(Cand, U)
    if key not in Cardinality or Cardinality[key] is None:
        card = CardOfPartition(Cand, df)
        Cardinality[key] = card
#    print("card: ", Cardinality[key])
    return Cardinality[key]

def f(C_km1, df, Closure, U, Cardinality, keys=None, fds=None):
    #import time
    
    # Set F to null list; Initialize U_c to remaining columns in data frame
    F = []; U_c = list(df.head(0));
    
    # Identify the subsets whose cardinality of partition should be tested
    SubsetsToCheck = [list(Subset) for Subset in set([frozenset(Candidate + [v_i]) for Candidate in C_km1 for v_i in list(set(U_c).difference(Closure[binaryRepr.toBin(Candidate, U)]))])];
    #print("subset length: ", SubsetsToCheck)
    # Add singleton set to SubsetsToCheck if on first k-level
    if len(C_km1[0]) == 1: SubsetsToCheck += C_km1;
    #t1 = time.time()
    # Iterate through subsets mapped to the Cardinality of Partition function
    # for Cand, Card in zip(SubsetsToCheck, map(CardOfPartition, SubsetsToCheck, [df]*len(SubsetsToCheck))):
    #     # Add Cardinality of Partition to dictionary
    #     Cardinality[binaryRepr.toBin(Cand, U)] = Card;

    # Iterate through candidates of C_km1
    #t2 = time.time()
    #print("find 1: ", t2 - t1, len(Cardinality))
    if keys is not None:
        keys_set = [set(k) for k in keys]
    for Candidate in C_km1:
        
        #print("CANDIDATE: ", set(Candidate))
        if keys is not None:
            overlap = [k for k in keys_set if k.issubset(set(Candidate))]
            if len(overlap) > 0:
                continue
        if get_card(Cardinality, Candidate, U, df) == 0:
            continue
        avg_vc = len(df) / get_card(Cardinality, Candidate, U, df) 
        #print("AVERAGE VALUE COUNT", Candidate, avg_vc)
        # it's a key
        if avg_vc == 1:
            if keys is not None and set(Candidate) not in keys_set:
                keys.append(Candidate)
        # if avg_vc <= 1.5:
        #     continue
        # Iterate though attribute subsets that are not in U - X{+}; difference b/t U and inclusive closure of candidate    
        for v_i in list(set(U_c).difference(Closure[binaryRepr.toBin(Candidate, U)])):
            # Check if the cardinality of the partition of {Candidate} is equal to that of {Candidate, v_i}
            if get_card(Cardinality, [v_i], U, df) == 0:
                continue
            v_i_card = get_card(Cardinality, [v_i], U, df)
            cand_card = get_card(Cardinality, Candidate + [v_i], U, df)
            collision_prob = (1.0 / v_i_card) ** (len(df) - cand_card)
            # if v_i == "price_p1_fix":
            #     print(Candidate, v_i, collision_prob, 1.0 / get_card(Cardinality, [v_i], U, df), (len(df) - get_card(Cardinality, Candidate + [v_i], U, df)))            
            # print("v_i", v_i, collision_prob, v_i_card)
            
            # if collision_prob > 0.01:
            #     continue
            if get_card(Cardinality, Candidate, U, df)  == get_card(Cardinality, Candidate + [v_i], U, df):
                # Add attribute v_i to closure
                Closure[binaryRepr.toBin(Candidate, U)].add(v_i)
                # Add list (Candidate, v_i) to F
                F.append([tuple(Candidate), v_i]);
    #t3 = time.time()
    #print("find 2: ", t3 - t2)
    return Closure, F, Cardinality;
