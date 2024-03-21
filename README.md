[![CodeQL](https://github.com/RoopeLuukkainen/ASPA/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/RoopeLuukkainen/ASPA/actions/workflows/codeql-analysis.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3898126.svg)](https://doi.org/10.5281/zenodo.3898126)

ASPA - Abstrakti SyntaksiPuu Analysaattori 
==========================================
Abstrakti SyntaksiPuu Analysaattori (ASPA) == Abstract Syntax Tree Analyser. It is a static analyser to support self-study and complying with recommended coding conventions at Fundamentals of Programming (CS1) course at LUT University. 

## Citation
If you wish to cite related research (preferred), cite a conference article at ICSE [DOI link](https://dl.acm.org/doi/10.1145/3510456.3514149), and same as text:
```
R. Luukkainen, J. Kasurinen, U. Nikula, V. Lenarduzzi, ASPA: A static analyser to support learning and continuous feedback on programming courses. an empirical validation, in: Proceedings of the ACM/IEEE 44th International Conference on Software Engineering: Software Engineering Education and Training, ICSE-SEET ’22, Association for Computing Machinery, New York, NY, USA, 2022, p. 29–39. doi:10.1145/3510456.3514149.
```

However to directly cite to this repository use "Cite this repository" to get Zenodo link.

## Repository structure

```bash
.
├── ASPA_main.py
├── misc
│   ├── ast_examples
│   └── preanalyse_structures
├── results
├── src
│   ├── BKT
│   ├── analysers
│   └── config
└── tests
    ├── AR_functions
    ├── MR_file_structure
    ├── OK_files
    ├── PK_exception_handling
    ├── PT_basic_command
    ├── TK_file_handling
    └── TR_data_structure
```

### ROOT
The root directory contains the main file, i.e. ASPA_main.py, which is used to run the program. In addition settings.json will be generated here after the initial execution. Finally there are repository related general files such as
1. .gitignore
2. LICENCE
3. README.md (this file)

### misc
In this directory, there are all the miscellaneous material, which did not belong to any other directory. This include helper documentation files e.g. 
1. examples of Abstract Syntax Trees (AST) which are used to check what type of tree some piece of codes created.
2. List of code structures which are detected with StructureDetector class.

### results
This directory is for the result files, i.e. output of analysis will be written here.

### src
This directory and its subdirectories contain all of the source code files, excluding ASPA_main.py.

### tests
This directory contains expected output files and subdirectories containing files which are analysed to get these results. **Each subdirectory is related to a single AST analyser, excluding OK_files**, which contain files with only valid structures, i.e. they should not create any errors, warnings or notes. Excpeted output files can be used as a primitive regression testing to check that previous checks did not fail due to the new check or change. No unit tests, yet.
1. AR_function == Function structure
2. MR_file_structure == Module/file structure
3. PK_exception_handling == Exception handling
4. PT_basic_command == Basic commands, e.g. loops, naming and unreachable code
5. TK_file_handling == File handling
6. TR_data_structure == Data structures e.g. classes (and objects)

