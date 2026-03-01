# FD Mine(r(U))

# Input: A relation r(U) over U = {v_1, ... ,v_m}

# Output: A set F of functional dependences over r(U)

# F = Null_Set

# E = Null_Set

# C_1 = U

# k = 1

#

# C_k = CalculatePartition(C_k, r(U))

# C_k = InitialClosure(C_k)

# while Cardinality(C_k) > 0:

# {

#   k += 1

#   C_k = Apriori_Gen(C_km1)

#   C_k = CalculatePartition(C_k, r(U))

#   C_k = InitialClosure(C_k)

#   F = F *Union* ObtainFDs(C_km1)

#   E = E *Union* ObtainEquivalences(C_km1, F)

#   C_k = Prune(C_km1, C_k, E)

# }

import time
__version__ = "0.1.7"


import pandas as pd

import sys, time, argparse, ntpath, pickle, csv

from .modules import *

from string import ascii_letters, ascii_uppercase

from .config import MAX_K_LEVEL


def main(df):

    letters = ascii_uppercase + u"ÄÖÜÇÁÉÍÓÚÀÈÌÒÙÃẼĨÕŨÂÊÎÔÛËÏ"

    # Define start time

    start_time = time.time()

    # Print line

    # print("Functional Dependencies: "); sys.stdout.flush();

    # Define header; Initialize k;
    
    U = list(df.head(0))
    k = 0
    # column which are not float type
    U_NF = [
        col for col in list(df.head(0)) if (not str(df[col].dtype).startswith("float")) and len(df[col].drop_duplicates()) < len(df[col])
    ]
    # keys = []
    # # for col in df.columns:
    # #     if len(df[col].drop_duplicates()) == len(df[col]):
    # #         keys.append([col])
    #print("non float columns", U_NF, len(U_NF), len(df))
    try:

        # Create dictionary to convert column names into alphabetical characters

        Alpha_Dict = {U[i]: letters[i] for i in list(range(len(U)))}

    except IndexError:

        print("Table exceeds max column count")

        sys.stdout.flush()

        return

    # Initialize lattice with singleton sets at 1-level

    C = [[[item] for item in U]] + [None for level in range(len(U) - 1)]
    # Create Generator to find next k-level attribute subsets
    pset = Apriori_Gen.powerset(U)
    Subset_Gen = (
        [x for x in pset if len(x) == k]
        for k in range(1, len(max(pset, key=len)) + 1)
    )
    # print("Subset_Gen", [s for s in next(Subset_Gen)])
    # Initialize Closure as Python dict

    Closure = {binaryRepr.toBin(Subset, U): set(Subset) for Subset in next(Subset_Gen)}

    # Initialize Cardinality as Python dict

    Cardinality = {element: None for element in Closure}

    # Create counter for number of Equivalences and FDs; initialize list to store FDs; list to store equivalences;

    Counter = [0, 0]
    FD_Store = []
    E_Set = []
    KEYs = []
    FDs = []

    while True:

        try:

            # Increment k; initialize C_km1

            k += 1
            C_km1 = C[k - 1]
            # print("C_km1", C_km1)
            # Initialize Closure at next next k-level; update dict accordinaly

            Closure_k = {
                binaryRepr.toBin(Subset, U): set(Subset) for Subset in next(Subset_Gen)
            }
            Closure.update(Closure_k)

            # Update Cardinality dict with next k-level

            Cardinality.update({element: None for element in Closure_k})

            if k > 1:

                # Dereference Closure and Cardinality at (k-2)-level

                for Subset in C[k - 2]:
                    del (
                        Closure[binaryRepr.toBin(Subset, U)],
                        Cardinality[binaryRepr.toBin(Subset, U)],
                    )

                # Dereference (k-2)-level

                C[k - 2] = None

            # Run Apriori_Gen to get k-level Candidate row from (k-1)-level Candidate row

            # Run GetFDs to get closure and set of functional dependencies
            KEYs = None
            Closure, F, Cardinality = GetFDs.f(C_km1, df, Closure, U, Cardinality, KEYs)
            

            # Print out FDs
            for FunctionalDependency in F:

                # Store well-formatted FDs in empty list

                FD_Store.append(
                    [
                        "".join(
                            sorted([Alpha_Dict[i] for i in FunctionalDependency[0]])
                        ),
                        Alpha_Dict[FunctionalDependency[1]],
                    ]
                )
                # Create string for functional dependency
                # print("FunctionalDependency[0]", FunctionalDependency[0], FunctionalDependency[1])
                # String = "{" + ", ".join(FunctionalDependency[0]) + "} -> {" + str(FunctionalDependency[1]) + "}"
                FDs.append((FunctionalDependency[0], FunctionalDependency[1]))
                # Print FD String

                # print(String); sys.stdout.flush();
            # Break while loop if k-level reaches level set in config

            if k is not None and MAX_K_LEVEL == k:
                break
            
            C_k = Apriori_Gen.oneUp(C_km1, U_NF)

            # Run Obtain Equivalences to get set of attribute equivalences

            E = ObtainEquivalences.f(C_km1, F, Closure, U)

            # Run Prune to reduce next k-level iterateion and delete equivalences; initialize C_k
            C_k, Closure, df = Prune.f(C_k, E, Closure, df, U, U_NF)
            C[k] = C_k

            # Increment counter for the number of Equivalences/FDs added at this level

            Counter[0] += len(E)
            Counter[1] += len(F)
            E_Set += E
            # Break while loop if cardinality of C_k is 0

            if not len(C_k) > 0:
                break

        except StopIteration:
            break

    # Print equivalences

    # print("\n" + "Equivalences: "); sys.stdout.flush();

    # Iterate through equivalences returned

    # for Equivalence in E_Set:

    # Create string for functional dependency

    # String = "{" + ", ".join(Equivalence[0]) + "} <-> {" + ", ".join(Equivalence[1]) + "}"

    # Print equivalence string

    # print(String); sys.stdout.flush();

    # Print out keys

    # print("\n" + "Keys: "); sys.stdout.flush();

    # Get string of column names sorted to alphabetical characters

    SortedAlphaString = "".join(sorted([Alpha_Dict[item] for item in Alpha_Dict]))

    # Run required inputs through keyList module to determine keys with

    keyList = keyRun.f(U, SortedAlphaString, FD_Store)

    # Iterate through keys returned

    # for key in keyList:

    #     # Print keys

    #     print(str(key)); sys.stdout.flush();

    # Create string to give user info of script
    """
    checkInfoString = str("\n" + "Time (s): " + str(round(time.time() - start_time, 4)) + "\n"

            + "Row count: " + str(df.count()[0]) + "\n" + "Attribute count: " + str(len(U)) + "\n"

            + "Number of Equivalences: " + str(Counter[0]) + "\n" + "Number of FDs: " + str(Counter[1]) + "\n"

            "Number of FDs checked: " + str(GetFDs.CardOfPartition.calls))
    """
    # Print elapsed time

    # print(checkInfoString); sys.stdout.flush();
    # print(type(keyList[0]))
    # print("KEYS: ", KEYs, keyList)
    return FDs, E_Set, keyList


def test_main():
    rnames = ["user_id", "movie_id", "rating", "timestamp"]
    ratings = pd.read_table("./files/ratings.dat", sep="::", header=None, names=rnames)
    unames = ["user_id", "gender", "age", "occupation", "zip"]
    users = pd.read_table("./files/users.dat", sep="::", header=None, names=unames)
    mnames = ["movie_id", "title", "genres"]
    movies = pd.read_table("./files/movies.dat", sep="::", header=None, names=mnames)
    main(movies)


# test_main()
