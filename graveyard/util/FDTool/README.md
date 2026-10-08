## README: Algorithm to mine for functional dependencies, equivalences and candidate keys

### Description: 
Ported to Python3

FDTool is a Python command-line application that mines functional dependencies, equivalences and
candidate keys from datasets read in from .csv, .txt, and .pkl files.

### Original Authors' Paper 
Buranosky M, Stellnberger E, Pfaff E, Diaz-Sanchez D, Ward-Caviness C. 
FDTool: a Python application to mine for functional dependencies and candidate keys in tabular data. F1000Res. 2018 Oct 19;7:1667. 
doi: 10.12688/f1000research.16483.2. PMID: 31069050; PMCID: PMC6489977.

### Dependencies:

  1. [Python3](https://www.python.org/) (version 3.10 or later recommended)

  2. [Pandas](https://pandas.pydata.org/) pip install pandas

### Configuration:

Edit ```REPO\fdtool\config.py``` prior to building setup to
change preset time limit or max k-level. Include (optional) custom outfile
name after command to run application.

### Build setup:
```
$ git clone https://github.com/ligonliu/FDTool.git
$ cd FDTool
$ python setup.py install
```

### Run Application:
```	
$ fdtool /path/to/file
```

### Sample Data:
Please refer to the [original repository](https://github.com/USEPA/FDTool/tree/master/data)

### Sample Output:
```
~/FDTool$ fdtool data/input/Table1.csv 

Reading file: 
data/input/Table1.csv

Functional Dependencies: 
{A} -> {D}
{D} -> {A}
{C, E} -> {A}
{C, E} -> {D}
{E, B} -> {A}
{E, B} -> {D}
{A, B} -> {E}

Equivalences: 
{A} <-> {D}
{E, B} <-> {A, B}

Keys: 
{B, C, E}
{B, C, D}
{A, B, C}

Time (s): 0.0121
Row count: 7
Attribute count: 5
Number of Equivalences: 2
Number of FDs: 7
Number of FDs checked: 22

```

### DOI Badge:
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3245414.svg)](https://doi.org/10.5281/zenodo.3245414)

### Notes:
Module ```REPO/fdtool/modules/dbschema``` released under C-FSL license 
and copyright held by Elmar Stellnberger. It is modified for Python3 compatibility.





