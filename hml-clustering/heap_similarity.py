import os
import itertools
import networkx as nx
from collections import Counter
from helpers import *

GROUND_TRUTH = ["atmel_6lowpan_udp_tx.bin", "csaw_esc19_csa.bin", "csaw_esc19_csb.bin", "expat_panda.bin", "Nucleo_blink_led.bin", "nxp_lwip_http.bin", "nxp_lwip_tcpecho.bin", "nxp_lwip_udpecho.bin", "p2im_car_controller.bin", "p2im_console.bin", "p2im_controllino_slave.bin", "p2im_drone.bin", "p2im_gateway.bin", "rf_door_lock.bin", "samr21_http.bin", "stm32_tcp_echo_client.bin", "stm32_tcp_echo_server.bin", "stm32_udp_echo_server.bin", "st-plc.bin", "thermostat.bin"]

# This is the list of name of tested blobs
TESTED = [
    "AC603_0101_V0.9.18_191114_1131.bin@2d2b364eb14d6ed089f80a9199d1955b",
    "BSW20204006.bin@be06d703962921f9bed8f372da5d72fc",
    "AC603_VIITA_BT_GS_V058_180414_1610.bin@a851bd8ff3080c563ecbfcfa61ba9147",
    "Exakt_Pedal_Radio_Firmware.bin@33d1345af50c399361f9d5fce0567056",
    "BSRLWK_h10_s9_20191124.bin@caa904fd25e50e8f135e58c43bee72fa",
    "BME-100.bin@57a8bcdd902053b7e20d7ebe1b32ded3",
    "bsafebeacon-S110.bin@e3488f240bb3283abb3be12243aa1604",
    "ICP_NRF52.bin@6b7cb12a8603e63113063f9690b5d228",
    "Hoot_release_pca10040.bin@87ce52ffbf0e4d807a4955b79287ca50",
    "nrf52832_xxaa_s132.bin@737076ab61cafd33cd86c8d437d2d9ac",
    "dddock_app_dock.bin@d2f576b0f652483b9f1a6af975180d8f",
    "BLERemote.bin@c7bbfe140ae7c72cdfbf503f1f28565b",
    "nrf52832_xxaa.bin@000d8d55c139962a8673c03a943b9b3d",
    "app_fw_RELEASE.bin@a4fabdef2a6b01e2589643672e2fe63c",
    "trigno_update_v040.024_T014.bin@12f39c5a9bff0421bf21fbea9ece20ef",
    "LRIP_nRF52_release.bin@9c152a025cc68dd2860e52582a536e95",
    "qtBrainoad_Car_Release_oad.bin",
    "pavlok_2_2008_0930.bin@739ef00cd2a6a808b920ee686eec7730",
    "nrf52832_xxaa.bin@589c2202be981bb90e9d95da769cc884",
    "Bond_Gen2.bin@5ff86dd6a17f86ab42060a64a4e678c4",
    "LinOn_Pro_RC18.bin@94ee078b55bd3063b6e387f26b7a1c98",
    "BP_application.bin@1175eccf7b2129c1dd8b6507b92c880e",
    "plugin_.bin@e6f47c7e7b95d320c7b082271a28c327",
    "ble5_project_zero_cc13x2r1lp_app_FlashROM_Release_oad.bin",
    "new_bin.bin",
    "nrf52832_xxaa.bin@c37602527d630b71e552b4e068d645fb",
    "fw-qcpr-sensor-mk3_release_0.45.1.69.bin@eece1af0257d195f2da2e9e621bdadd3",
    "sma10b_firmware.bin@4e84107c04eaf072ea37bcc207155101",
    "Exakt_Pedal_Radio_Firmware.bin@3dd4d4906fb7ec7595a5b1b7d7412612",
    "plot.bin@1050de8c98acf89e8c2dba6fc1d9f3e4",
    "bicult_ble_sdk15_sd_132v6.bin@8e6cd8526dc3151d34ddf53466789627",
    "tag-firmware.bin@4acb76b9d48aa82f3a3f4282f8482731",
]

NAME = 'FINALFINAL_MR'


def shorten(label):
    if '@' in label:
        a, b = label.split('@')        
        return a[:6] + '..@' + b
    else:
        return label[:16]
    
def add_node(G, allocator):
    target = allocator['target']
    label  = allocator['label']
    malloc = allocator['malloc']
    working_ps = allocator['working_ps']
    truth  = int(label in GROUND_TRUTH)    
    found  = int(allocator['malloc'] != 0)
    print("adding node %s malloc: %x working_ps: %s truth: %s found: %d" % (label, malloc or 0, working_ps or 0, truth, found))
    G.add_node(target, label=label, truth=truth, found=found, malloc=malloc, working_ps=working_ps, inferred=[], viz={})

def add_edge(G, t1, t2, a1, a2, similarity, confidence, inferred):
    log = '%-40s %-40s 0x%06x 0x%06x %.3f %.3f inferred:0x%06x' % (get_label(t1), get_label(t2),
                                                                   a1, a2,
                                                                   similarity or 0, confidence or 0, inferred or 0)

    if similarity is None or (similarity < 0.7 or confidence < 0.7):
        print(log + ' [not added]')
        return False

    print(log)
    G.add_edge(t1, t2,
               label=str(similarity),
               weight=10,
               similarity=similarity,
               confidence=confidence,
               missing=1 if inferred else 0,
               viz={})
    return True

def find_node(G, x):
    for n in G.nodes:
        if x in n:
            return n

# Manual refinement as explained in the paper.
def add_manual_edges(G):
    manual_edges = [
        ("sensor.bin@3fce0fc868b7d66ccf5fbf1aae9dff73",   "bsafebeacon-S110.bin@e3488f240bb3283abb3be12243aa1604", True),
        ("freedrum.bin@12546bf801d8f28458e4b78665dec513", "bsafebeacon-S110.bin@e3488f240bb3283abb3be12243aa1604", True),
        ("L38I.bin@db0c4c906e8a3e12bf574ebd9053d3b1",     "fw-qcpr-sensor-mk3_release_0.45.1.69.bin@eece1af0257d195f2da2e9e621bdadd3", True),
        ("BLE_BADGE_OTA_v1_7.bin@ddcce855ee3d500df95c337d345be2ed", "tag-firmware.bin@4acb76b9d48aa82f3a3f4282f8482731", True),
        ("Movesense.bin@7da3e79d36043c4a6a4008f22dcefcfd", "trigno_update_v040.024_T014.bin@12f39c5a9bff0421bf21fbea9ece20ef", True),
        ("fw_resusci_junior_ble.bin@dafc52fa89c6a1266e61e89be37aca9a", "LRIP_nRF52_release.bin@9c152a025cc68dd2860e52582a536e95", True),
        ("DA_Embedded.bin@cd01029d61c802984f8e7a78dcd3e371", "nrf52832_xxaa.bin@589c2202be981bb90e9d95da769cc884", True),
        ("qtBrainoad_Car_Release_oad.bin", "mia2_oad.bin", True),
        ("nxp_lwip_http.bin", "nxp_lwip_tcpecho.bin", True),
        ("fw-qcpr-sensor-mk3_release_0.45.1.69.bin@eece1af0257d195f2da2e9e621bdadd3", "SPRINT_V1.57.bin@74868438318a967841fe8174d36f409c", True),
        ("plugin_.bin@e6f47c7e7b95d320c7b082271a28c327", "fw_resusci_junior_ble.bin@dafc52fa89c6a1266e61e89be37aca9a", True),
        ("BB_Project.bin@c5639c8752da08ed04c0136715dcfd2e", "bicult_ble_sdk15_sd_132v6.bin@8e6cd8526dc3151d34ddf53466789627", True),
        ("BBFW_2.1.1.7.bin@0ad456fe540a8b49cd5278f205e2e6d6", "bicult_ble_sdk15_sd_132v6.bin@8e6cd8526dc3151d34ddf53466789627", True),
        
        ("nrf52832_xxaa.bin@78187557902d12571d98e31bb0b92e6d", "SPRINT_V1.57.bin@74868438318a967841fe8174d36f409c", True),
        ("nrf52832_xxaa.bin@030448d2b1faf6deacbcc6274057828f", "SPRINT_V1.57.bin@74868438318a967841fe8174d36f409c", True),
        ("nrf52832_xxaa.bin@7dcf1faea39cd18b3ea91b94c824e950", "SPRINT_V1.57.bin@74868438318a967841fe8174d36f409c", True),
        ("nrf52832_xxaa.bin@dfe6e4aa1ecd9c766fd78d6571ad3f15", "SPRINT_V1.57.bin@74868438318a967841fe8174d36f409c", True),
        ("nrf52832_xxaa.bin@14325a9d1ef867d300aca33e055f5952", "SPRINT_V1.57.bin@74868438318a967841fe8174d36f409c", True),
        
    ]

    frontier = ["nrf52832_xxaa.bin@78187557902d12571d98e31bb0b92e6d", "nrf52832_xxaa.bin@030448d2b1faf6deacbcc6274057828f", "nrf52832_xxaa.bin@7dcf1faea39cd18b3ea91b94c824e950",
                "nrf52832_xxaa.bin@dfe6e4aa1ecd9c766fd78d6571ad3f15", "nrf52832_xxaa.bin@14325a9d1ef867d300aca33e055f5952"]
    
    for f in frontier:
        t = find_node(G, f)
        for neighbor in list(G.neighbors(t)):
            G.remove_edge(t, neighbor)
            
    for t1, t2, add in manual_edges:
        similarity, confidence = 1,1
        t1 = find_node(G, t1)
        t2 = find_node(G, t2)
        if not t1 or not t2:
            print(t1, t2)
            assert(False)
        if add:
            G.add_edge(t1, t2,
                       label=str(similarity),
                       weight=similarity*10,
                       similarity=similarity,
                       confidence=confidence,
                       missing=0,
                       manual=1,
                       viz={})
        else:
            try:
                G.remove_edge(t1, t2)
            except:
                print("EDGE NOT FOUND: %s %s" % (t1, t2))
                
def main():
    G = nx.Graph()
    allocators = []

    # Adding nodes
    for target in get_targets():
        # target is the path to a firmware folder
        # e.g.: /wild/firmware_name.bin/
        #       this folder must contain the hb_analysis folder and the hb_state.json 
        try:
            # allocator is the final_allocator detected by Heapster analysis 
            allocator = get_hml(target)
        except FileNotFoundError:
            continue
        print('[allocator] %s 0x%x' % (allocator['label'],
                                       allocator['malloc']))
        allocators.append(allocator)
        add_node(G, allocator)

    # Adding edges
    for primary, secondary in list(itertools.combinations(allocators, 2)):
        t1, t2 = primary['target'], secondary['target']
        a1, a2 = primary['malloc'], secondary['malloc']
        if not a1 and not a2:
            continue

        if a1 and a2:
            similarity, confidence = get_functions_similarity(t1, t2, a1, a2)
            inferred_address = 0
        else:
            similarity, confidence, inferred_address = find_similar_function(t1, t2, a1, a2)

        added = add_edge(G, t1, t2, a1, a2, similarity, confidence, inferred_address)

        if added and (not a1 or not a2):
            inferred_node = t1 if not a1 else t2
            G.nodes[inferred_node]['inferred'].append(hex(inferred_address))


    add_manual_edges(G)

    gray_nodes = []
    for node in list(G.nodes()):
        label = G.nodes[node]['label']
        truth = G.nodes[node]['truth']
        found = G.nodes[node]['found']
        # We don't delete ground truth nodes, nodes with edges
        # and nodes where HB found a heap
        if truth or G.degree[node] > 0 or found:
            G.nodes[node]['gray'] = 0
            continue

        if G.nodes[node]['working_ps'] == None:
            print("xyz: %s" % label)

        G.nodes[node]['gray'] = 1
        gray_nodes.append(node)

    # Deleting nodes
    save_pickle(G, 'graphs/%s.pickle' % NAME)
    G.remove_nodes_from(gray_nodes)

    # Stats
    found = 0
    for node in G.nodes():
        if G.nodes[node]['found']:
            found += 1
            print("[true positive] %-30s 0x%06x" % (G.nodes[node]['label'],
                                                    G.nodes[node]['malloc']))
        else:
            best = best_neighbor(G, node)
            if not best:
                print("[unclear] No function of %s matches a true positive" % G.nodes[node]['label'])
                continue
            
            edge = G.edges[best, node]            
            log = "[false negative] %-30s %s " % (G.nodes[node]['label'],
                                                  Counter(G.nodes[node]['inferred']).most_common(3))
            log += "best_match: %-30s 0x%06x %.3f" % (G.nodes[best]['label'],
                                                      G.nodes[best]['malloc'],
                                                      edge['similarity'])
            print(log)

    print('Found: %d' % found)
    print('Not found: %d' % (len(G.nodes()) - found))

    set_ccomponents(G)
    
    for node in G.nodes():
        label = G.nodes[node]['label']
        truth = G.nodes[node]['truth']

        if truth:
            G.nodes[node]['label'] = label.replace('.bin', "")
            continue

        # Was this node tested?
        if any(i in node for i in TESTED):
            G.nodes[node]['tested'] = True
            G.nodes[node]['label'] = shorten(label)
        else:
            G.nodes[node]['tested'] = False            
            G.nodes[node]['label'] = ""

                    
    # Save graph
    for n in G.nodes():
        del G.nodes[n]['inferred']
        del G.nodes[n]['working_ps']
    save_graph(G, '%s.gexf' % NAME)

if __name__ == '__main__':
    main()
