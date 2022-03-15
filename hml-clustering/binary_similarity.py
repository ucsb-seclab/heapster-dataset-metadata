import os
import glob
import itertools
import networkx as nx
from helpers import *

def hb_found_malloc(target):
    allocator = get_hml(target)
    return allocator['malloc'] != 0


def main():
    targets = get_targets()

    # Adding nodes
    G = nx.Graph()

    for target in targets:
        label = get_label(target)
        found = hb_found_malloc(target)
        G.add_node(target, label=label, found=found)

    # Adding edges
    for primary, secondary in sorted(list(itertools.combinations(targets, 2))):
        similarity, confidence = get_file_similarity(primary, secondary)

        if similarity is None:
            continue

        if similarity >= 0.4 and confidence >= 0.8:
            G.add_edge(primary, secondary,
                       weight=similarity,
                       confidence=confidence)


    # Save graph
    set_ccomponents(G)
    save_graph(G, 'full.gexf')

if __name__ == "__main__":
    main()
