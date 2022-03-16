This folder contains the code used to clusterize the HMLs discovered in our dataset as explained in the [paper](https://degrigis.github.io/bins/heapster.pdf).

# Requirements

1. IDApro 
2. BinDiff 

# Usage

1. Install the Heapster IDA loader plugin by dropping `scripts/ida_loader.py` in your `/ida/loaders/` folder.
2. Move firmware samples you want to classify in `./firmware`. The folder should be structured in the following way:
   ```
   ./firmware/
      -> <FIRMWARE_NAME1.bin>
         -> /hb_analysis
            -> /hb_state.json 
         -> <FIRMWARE_NAME1.bin>
      -> <FIRMWARE_NAME2.bin>
         -> /hb_analysis
            -> /hb_state.json 
         -> <FIRMWARE_NAME2.bin>
      -> ...
   ```
2. Generates the .idb and the file needed from BinDiff to perform the binary diffing.
   * `/scripts/create_idbs.sh`
3. This script does the binary comparison between ALL the functions of any pair of blobs in `./firmware/`
   It outputs n^2 number of SQLite databases containing the diffing information
   * `python3 /scripts/compare_all.py` 
4. Generate the similarity graph of the discovered HMLs
   * `python3 /scripts/heap_similarity.py` 
5. Generates the similarity graph considering the whole firmware images 
   * `python3 /scripts/binary_similarity.py`


# Extra

In `./artifacts` you can find the latest version of the graph as presented in the paper. You can use [Gephi](https://gephi.org/) to visualize it!