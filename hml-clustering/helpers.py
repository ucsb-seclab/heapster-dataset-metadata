import os
import glob
import json
import pickle
import sqlite3
import networkx as nx
from os.path import basename

SCRIPTDIR = os.path.dirname(os.path.realpath(__file__))
CACHEDIR  = os.path.join(SCRIPTDIR, 'cache')

# Queries
def get_file_similarity(primary, secondary):
    conn = connect_db(primary, secondary)
    if not conn:
        return None, None
    cur  = conn.execute('SELECT ROUND(similarity, 3), ROUND(confidence, 3) FROM metadata')
    return cur.fetchone() or (None, None)

def get_functions_similarity(primary, secondary, address1, address2):
    conn = connect_db(primary, secondary)
    if not conn:
        return None, None

    cur  = conn.execute('SELECT ROUND(similarity, 3), ROUND(confidence,3) FROM function where address1=? and address2=?', (address1, address2))

    return cur.fetchone() or (None, None)

def find_similar_function(primary, secondary, address1, address2):
    conn = connect_db(primary, secondary)
    if not conn:
        return None, None

    if address1:
        cur  = conn.execute('SELECT ROUND(similarity, 3), ROUND(confidence,3), address2 FROM function where address1=? ORDER BY similarity', (address1,))
    if address2:
        cur  = conn.execute('SELECT ROUND(similarity, 3), ROUND(confidence,3), address1 FROM function where address2=? ORDER BY similarity', (address2,))

    return cur.fetchone() or (None, None, None)

def save_pickle(o, path):
    with open(os.path.join(SCRIPTDIR, path), 'wb') as f:
        pickle.dump(o, f)

def load_pickle(path):
    with open(os.path.join(SCRIPTDIR, path), 'rb') as f:
        return pickle.load(f)

def get_targets():
    firmware    = os.path.realpath(os.path.join(SCRIPTDIR, 'firmware/'))
    targetsdirs = glob.glob(firmware + '/*')
    targets     = [os.path.join(d, basename(d)) for d in targetsdirs]
    return sorted(targets)

# Database
def get_db(primary, secondary):
    primary, secondary = sorted([primary, secondary])
    db = os.path.join(CACHEDIR, '%s_vs_%s.BinDiff' % (basename(primary),
                                                      basename(secondary)))
    if os.path.isfile(db) and os.stat(db).st_size:
        return db

def connect_db(primary, secondary):
    db = get_db(primary, secondary)
    return sqlite3.connect(db) if db else None

# Graph
def best_neighbor(G, node):
    edges = G[node]
    if len(edges) == 0:
        return
    best  = max(edges.items(), key=lambda x: x[1]['similarity'])[0]
    return best


def rgba(r, g, b, a):
    return {'r': r, 'g': g, 'b': b, 'a': a}

# Sets an attribute that represents the connected componenets
def set_ccomponents(G):
    attributes = {}
    colors = [
        rgba(255,185,168,255),
        rgba(152,224,193,255),
        rgba(214,206,234,255),
        rgba(224,204,149,255),
        rgba(255,190,215,255),
        rgba(186,223,146,255),
        rgba(164,221,232,255),
        rgba(217,203,186,255),
        rgba(255,200,127,255),
        rgba(244,244,244,255), # Gray
        rgba(244,244,244,255), 
        rgba(244,244,244,255),
        rgba(244,244,244,255),
        rgba(244,244,244,255),
    ]

    connected_components = [list(c) for c in nx.connected_components(G)]
    connected_components = sorted(connected_components, key=lambda x: len(x), reverse=True)
    for index, component in enumerate(connected_components):
        print('%d %d' % (index, len(component)))
        for node in component:
            attributes[node] = index
            G.nodes[node]['viz']['color'] = colors[index]
            for edge in G.edges(node):
                G.edges[edge]['viz']['color'] = colors[index]

    for node in G.nodes():
        if G.nodes[node]['truth']:
            G.nodes[node]['viz']['color'] = rgba(238, 238, 0, 255)
            
    nx.set_node_attributes(G, attributes, "component")

def save_graph(G, name):
    nx.write_gexf(G, os.path.join(os.path.dirname(__file__), "graphs", name))

def get_label(target):
    name = basename(target)
    if '@' in name:
        return name[:name.index('@')+5]
    else:
        return name


# This is reading the hb_state.json file
def get_hml(target):
    hb_state_file  = os.path.join(os.path.dirname(target),
                                  'hb_analysis', 'hb_state.json')

    with open(hb_state_file) as f:
        hb_state = json.load(f)

    works = hb_state.get('allocator_works', 0)
    allocator = hb_state.get('final_allocator', {})
    allocator['working_ps'] = hb_state.get('working_pointer_sources') or None
    allocator['target'] = target
    allocator['label']  = get_label(target)
    if works:
        allocator['malloc'] = int(allocator['malloc'], 16) - 1
    else:
        allocator['malloc'] = 0

    return allocator
