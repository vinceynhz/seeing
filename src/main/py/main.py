"""
 :author: vic on 2023-10-04
"""
import logging
import json

import networkx as nx
import numpy as np
from flask import Flask, render_template, jsonify

import mitre

# creates a Flask application
app = Flask(__name__)

attack_source = None
tactics = []
groups = []


@app.route("/")
def root():
    return render_template('index.html')


@app.route("/data/organisms", methods=["GET"])
def get_groups():
    return jsonify(groups)


@app.route("/data/families", methods=["GET"])
def get_tactics():
    return jsonify(tactics)


@app.route("/graph/<group_id>", methods=["GET"])
def get_graph(group_id):
    # get the techniques
    techniques = mitre.techniques_by_group(attack_source, group_id)

    logging.debug(json.dumps(techniques))

    # create a map by tactic
    techniques_by_tactic = {t["x_mitre_shortname"]: [] for t in tactics}

    # assign techniques to each tactic
    for technique in techniques:
        for tactic in technique["tactics"]:
            if tactic not in techniques_by_tactic:
                techniques_by_tactic[tactic] = []
            techniques_by_tactic[tactic].append(tactic + "--" + technique["id"])

    graph = nx.Graph()
    graph_layers = []
    for tactic in techniques_by_tactic:
        num_techniques = len(techniques_by_tactic[tactic])
        if num_techniques == 0:
            continue
        G = nx.cycle_graph(techniques_by_tactic[tactic])
        # To add metadata to the nodes
        # for t in techniques_by_tactic[tactic]:
        #     G.nodes[t]['technique'] = t
        #     G.nodes[t]['tactic'] = tactic

        graph_layers.append(G)

    # now we need to connect layers among themselves
    for i in range(len(graph_layers)):
        # add the current node to the graph
        H = graph_layers[i]
        graph.add_nodes_from(list(H.nodes(data=True)))
        graph.add_edges_from(list(H.edges(data=True)))

        # see if we can connect it to the previous layer, which should already be present in the graph
        if i > 0:
            G = graph_layers[i - 1]
            for hnode in H:
                for gnode in G:
                    graph.add_edge(gnode, hnode, weight=5)

    # layout the whole thing
    pos = nx.spring_layout(graph, dim=3)
    # pos = nx.kamada_kawai_layout(graph, dim=3)
    pos = {k: np.around(pos[k] * 50, 2).tolist() for k in pos}
    for v in pos:
        graph.nodes[v]['pos'] = pos[v]

    nodes = dict(graph.nodes(data=True))
    edges = [(nodes[e[0]]['pos'], nodes[e[1]]['pos']) for e in list(graph.edges()) if e[0] != e[1]]

    result = {
        'nodes': nodes,
        'edges': edges
    }

    return jsonify(result)


@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404


def init():
    global attack_source
    global tactics
    global groups
    logging.basicConfig(format='%(asctime)s-%(levelname)s:%(message)s', level=logging.DEBUG)

    logging.info("Seeing is believing...")

    # For now we'll need a local copy of the MITRE Att&ck matrix. If this is parameter is not passed, the matrix will be
    # retrieved from the attach-stix-data GitHub repository
    # attack_source = mitre.init_mitre_matrix("../attack-stix-data/enterprise-attack/enterprise-attack.json")
    attack_source = mitre.init_mitre_matrix()
    tactics = mitre.extract_tactics(attack_source)
    groups = mitre.extract_groups(attack_source)

    app.run(host='0.0.0.0', debug=False)


# run the application
if __name__ == "__main__":
    init()
