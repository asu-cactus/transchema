#CalculatePartition.py Apriori_Gen (C_km1) - generates all
#                       possible candidates in C_k
#                       from the candidates in C_km1


# Create function to calculate power set
import itertools
def powerset(s):
    x = len(s)
    # Create list for powerset contents
    Powerset = []
    # for i in range(1 << x):
    #     p = [s[j] for j in range(x) if (i & (1 << j))]
    #     Powerset.append(p)
    #     print("powerset: ", i,  len(Powerset), p)
    for i in range(1,5):
        Powerset += [list(p) for p in list(itertools.combinations(s, i))]
        #print(len(Powerset))

    return Powerset;

def oneUp(C_km1, U_NF=None):

    # Flatten list to unique values
    flat_list = list(set([item for sublist in C_km1 for item in sublist]))
    if U_NF:
        flat_list = [p for p in flat_list if p in U_NF]
    #print(flat_list, len(flat_list))
    # Create generator containing all subsets of unique attributes
    #AttributeSubsets = (Subset for Subset in powerset(flat_list))
    AttributeSubsets = (Subset for Subset in [list(p) for p in list(itertools.combinations(flat_list, (len(next(iter(C_km1))) + 1)))] )
    return [Subset for Subset in AttributeSubsets]
    # Generate list of subsets at one level up from input
    #return [Subset for Subset in AttributeSubsets if len(Subset) == (len(next(iter(C_km1))) + 1)];
    
def oneDown(C_k, U_NF=None):

    
    # Flatten list to unique values
    flat_list = list(set([item for sublist in C_k for item in sublist]))
    if U_NF:
        flat_list = [p for p in flat_list if p in U_NF]
    # Create generator containing all subsets of unique attributes
    #AttributeSubsets = (Subset for Subset in powerset(flat_list))
    AttributeSubsets = (Subset for Subset in [list(p) for p in list(itertools.combinations(flat_list, (len(next(iter(C_k))) - 1)))] )
    return [Subset for Subset in AttributeSubsets]
    # Generate list of subsets at one level down from input
    #return [Subset for Subset in AttributeSubsets if len(Subset) == (len(next(iter(C_k))) - 1)]; 

