from netdiff import NetJsonParser
import networkx as nx
import itertools
import json


def ReadGrafoDaJson():
    netJSON = NetJsonParser(file='topology.json')
    grafo = netJSON.graph
    return grafo


def ContaCammini(G):
    GrafoOrigine = nx.read_graphml('rete.graphml')
    startingNodes = list(GrafoOrigine.nodes())

    NodiDopoEspansione = list(G.nodes())

    nodiInalterati = list(set(startingNodes) & set(NodiDopoEspansione))

    NodiEspansi = set(NodiDopoEspansione) - set(nodiInalterati)
    BC = dict.fromkeys(NodiEspansi, 0)

    for x, y in itertools.combinations(nodiInalterati, 2):
        cammino = list(nx.dijkstra_path(G, x, y, weight='weight'))

        for value in cammino:
            if(value in NodiEspansi):
                BC[value] += 1

    print json.dumps(BC, indent=4)


grafo = ReadGrafoDaJson()
ContaCammini(grafo)
