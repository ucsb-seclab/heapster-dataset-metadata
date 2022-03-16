This folder contains the code used to clusterize the HMLs discovered in our dataset as explained in the [paper](https://degrigis.github.io/bins/heapster.pdf).

# Requirements

1. IDApro 
2. BinDiff 

# Usage

1. Install the IDA plugin in `scripts/ida_loader.py` by dropping the loader in /ida/loaders/
2. `/scripts/create_idbs.sh`
   * This script generates the .idb and the file needed from BinDiff to perform the binary diffing.
3. `python3 /scripts/compare_all.py` 
   * This script does the binary comparison between ALL the functions of any pair of binary in ./firmware/
   * It outputs n^2 number of sqlite databases containing these information
4. `python3 /scripts/heap_similarity.py` 
   * This script generates the similarity graph of the discovered HMLs
5. `python3 /scripts/binary_similarity.py`
   * This script generates the similarity graph using the whole firmware images 
