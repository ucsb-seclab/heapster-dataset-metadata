# heapster-dataset-metadata
Collection of metadata for the firmware images used in Heapster

* `fw-load-confs`: contains configuration file to load the firmware images in our dataset inside angr.
* `fw-hml-ident-metadata`: contains the info collected by all the stages of Heapster: blob entry-point, blob base-address, basic function identified, pointer sources, malloc/free candidates, ...
* `fw-wild-heap-vulns`: this folder contains the SQLite dbs for the firmware blobs tested during the HMLs security evaluation.
* `hardware_example`: this folder contains the code and the exploit of the vulnerable firmware presented in the "Hardware Example" section of the paper.