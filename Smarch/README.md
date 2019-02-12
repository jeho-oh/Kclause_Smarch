# Smarch
Smarch is a tool to Uniformly Random Sample (URS) solutions of a propositional formula. For a given dimacs file, Smarch will count the number of solutions, generate a random number from 1 to number of solutions, and create a one-to-one mapping between a random number and a configuraiton.

## Prerequisites
Smarch relies on following tools:
* sharpSAT (): A exact model counting tool
* march_cu (): Solver based on cube-and-conquer algorithm

Source files for both tools are included in the repository.
You can build each tool by running make.

Smarch python script uses following additional packages: anytree, pycosat

## How to run
```python
python3 smarch.py -c <constfile> -o <outputdir> -s  <dimacsfile> <samplecount>
```
* dimacsfile: Location of the dimacs file.
* samplecount: Number of samples to create.
* constfile: Location of the constraint file. (default: none)
* outputdir: Directory to create the output files. (default: (dimacs location)/smarch) 

## Output
On the specified outputdir, samples.txt file lists the samples.
Each line represents a sample, which is a list of variables.
Positive value means true is assigned, negative value means false is assigned.

